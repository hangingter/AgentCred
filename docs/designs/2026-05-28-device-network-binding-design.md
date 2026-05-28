# Agent-Score 设备与网络绑定设计

> 目标：在现有 `Agent DID → Principal DID` 问责链基础上，增加运行时 **设备（TEE/SE/TPM）** 与 **网络（IP/ASN/Geo）** 绑定，防止 Agent 私钥被盗用后在任意机器/任意网络上通过握手。

## 1. 设计原则

1. **密钥不出安全域**：Agent 签名密钥由 TEE/SE/TPM 管理，attestation 证明私钥确实在指定设备中。
2. **运行时校验**：每次 A2A 握手都携带最新设备 attestation，而不仅是注册时一次性绑定。
3. **网络指纹辅助**：IP 网段、ASN、Geo 作为软绑定，异常漂移触发额外 Principal 二次签名或直接拒绝。
4. **可组合策略**：不同业务场景可选择不同绑定强度（强绑定 / 注册绑定 / 仅溯源）。
5. **不破坏现有协议**：作为 Agent Card `x-agent-score` 的可选扩展字段，不携带时走原有信用分路径。

## 2. 核心数据模型

### 2.1 DeviceAttestation（设备证明）
由设备安全硬件（TEE/SE/TPM）或远程验证服务签发，证明：
- 特定 Agent DID 私钥确实在该设备中
- 设备硬件型号、固件版本、安全状态（是否解锁 root、是否有调试接口）
- 可选：设备唯一标识（公钥哈希 / 序列号哈希）

```json
{
  "attestation_type": "tee_sgx_ecdsa_qe3",
  "device_pubkey_hash": "0xabc...",
  "agent_did": "did:ethr:0x2105:0x...",
  "nonce": "0x...",
  "timestamp": 1780000000,
  "quote": "base64-encoded-quote",
  "signature": "base64-encoded-attestation-signature"
}
```

### 2.2 NetworkFingerprint（网络指纹）
由 Agent 运行时采集，或由可信网关/中继节点背书：
- `ipv4` / `ipv6` 前缀（不记录完整 IP，保护隐私）
- `asn`（自治系统号）
- `country_code`（ISO 3166-1 alpha-2）
- `is_anonymous_proxy` / `is_tor_exit` / `is_vpn`（由第三方服务判断）

```json
{
  "ipv4_prefix": "203.0.113.0/24",
  "asn": 12345,
  "country_code": "SG",
  "is_vpn": false,
  "timestamp": 1780000000,
  "observer_did": "did:web:gateway.example.com"
}
```

### 2.3 DeviceBindingVC（设备绑定凭证）
由 Device Authority（白名单）签发，有效期建议 **24 小时**（远短于 CreditVC 的 30 天），确保持续在线验证：

```json
{
  "@context": ["https://www.w3.org/ns/credentials/v2", "https://agent-score.org/v1"],
  "type": ["VerifiableCredential", "AgentDeviceBindingCredential"],
  "issuer": "did:web:device-authority.example.com",
  "issuanceDate": "2026-05-28T00:00:00Z",
  "expirationDate": "2026-05-29T00:00:00Z",
  "credentialSubject": {
    "id": "did:ethr:0x2105:0x...",
    "principal": "did:web:acme.com",
    "device_attestation": { /* 2.1 结构 */ },
    "network_fingerprint": { /* 2.2 结构 */ },
    "binding_level": "strong"
  },
  "proof": {
    "type": "AgentScoreJWS2026",
    "jws": "..."
  }
}
```

## 3. 协议扩展点

### 3.1 Agent Card 扩展
在 `x-agent-score` 中新增可选字段：
```json
{
  "x-agent-score": {
    "did": "...",
    "principal": "...",
    "credit_vc": { ... },
    "device_binding_vc": { ... },   // 新增
    "network_fingerprint": { ... }  // 新增（可选，运行时采集）
  }
}
```

### 3.2 AgentPolicy 扩展
新增设备绑定策略字段：
```python
@dataclass(frozen=True)
class AgentPolicy:
    min_credit_score: int = 600
    min_tier: str = "B"
    max_violation_90d: int = 2
    trusted_issuers: Set[str] = None
    require_device_binding: bool = False          # 新增
    min_binding_level: str = "registration"       # registration / runtime / strong
    allowed_countries: Set[str] = None            # 新增
    blocked_asns: Set[int] = None                 # 新增
    require_principal_co_sign_on_drift: bool = True  # 新增
```

### 3.3 Handshake 扩展
`verify_agent_card_credit` 增加设备绑定校验分支：
1. 如果 `policy.require_device_binding=True`，但 `card.device_binding_vc` 缺失 → 拒绝 `MISSING_DEVICE_BINDING`
2. 验证 DeviceBindingVC 的 issuer 在 `trusted_device_authorities` 白名单
3. 验证 DeviceBindingVC 的有效期（24 小时）
4. 验证 `device_attestation.agent_did == card.did`（设备确实绑定到该 Agent）
5. 验证 `network_fingerprint` 符合 `allowed_countries` / `blocked_asns` 策略
6. 如果网络指纹相对注册地发生漂移（国家变更 / ASN 变更），要求额外 Principal 签名或拒绝

### 3.4 Credit Engine 扩展
新增 `DeviceScore` 维度，权重建议 **100 分**（从现有 Principal 维度拆分，总权重保持 1000 不变）：

```
CreditScore = clamp(0, 1000,
    300                              // 基础分
  + 350 · BehaviorScore / 100        // 历史行为
  + 200 · StakeScore / 100           // 质押
  + 150 · EndorsementScore / 100     // 背书
  + 150 · ValidationScore / 100      // 第三方验证
  + 100 · DeviceScore / 100          // 新增：设备绑定强度
  +  50 · PrincipalScore / 100       // 原 150 降为 50
  - 400 · ViolationPenalty           // 违规扣分
)
```

`DeviceScore` 计算规则：
- `strong`（TEE 运行时 attestation + 24h VC）：100 分
- `runtime`（设备公钥签名 + 网络指纹匹配）：75 分
- `registration`（仅注册时绑定）：50 分
- `none`（无绑定）：0 分
- 网络漂移且无 Principal 二次签名：额外 -50 分

## 4. 实现范围（本次）

1. **协议层**：新增 `DeviceAttestation`、`NetworkFingerprint`、`DeviceBindingVC` 数据模型
2. **Credit Engine**：新增 `DeviceScore` 维度，调整权重，新增 reason code
3. **Middleware**：扩展 `AgentPolicy`、`AgentCard`、`verify_agent_card_credit` 支持设备绑定校验
4. **FastAPI Adapter**：透传 `device_binding_vc` 和 `network_fingerprint` 字段
5. **测试**：覆盖强绑定通过、缺失拒绝、网络漂移拒绝、设备分影响信用分

## 5. 非目标（后续版本）

- 真实 TEE/TPM 驱动集成（当前使用 mock attestation）
- 真实 IP/ASN/Geo 数据库集成（当前使用 mock fingerprint）
- Principal 二次签名的具体协议（当前只定义策略位）
- 链上 Device Registry（当前在链下 VC 层实现）
