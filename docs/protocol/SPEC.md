# Agent-Score Protocol Specification

> Version: 0.1.0-draft · Date: 2026-05-27
> Status: Draft for Review
> 在 Google A2A、ERC-8004、W3C DID/VC 之上扩展，构建 **银行级 Agent 信用体系** 与 **A2A 快速认证层**。

---

## 0. 设计原则

1. **不重造轮子**：身份层复用 W3C DID + ERC-8004，通信层对接 Google A2A v1.0，支付层对接 x402 / ERC-8183。
2. **链上轻、链下重**：链上只锚定身份、信用快照、违规记录、质押；交互流水链下存证，Merkle Root 上链。
3. **隐私优先**：默认支持 ZK 选择性披露（参考 ACTA），评分阈值证明不暴露具体分数。
4. **Sybil 抵抗双轨制**：Stake/Slash + Principal-DID 担保链 + 跨域背书多样性，三选二即满足。
5. **可问责**：每一次 A2A 交互都可回溯到 Principal（人或组织），违规记录跨注销持久化。

---

## 1. 术语

| 术语 | 含义 |
|---|---|
| **Agent** | 由 LLM/工作流驱动的自治实体，拥有独立 DID 与钱包地址。 |
| **Principal** | Agent 背后的责任主体（自然人 / 法人 / DAO），持有上级 DID。 |
| **Operator** | 部署运行 Agent 的运营方，可与 Principal 同体。 |
| **CreditScore** | Agent 的实时多维信用分（0–1000，类似 FICO）。 |
| **CreditVC** | 由 Credit Authority 签发的、可验证的信用凭证。 |
| **IPR (Interaction Proof Record)** | 双签的 A2A 交互证明记录。 |
| **Violation Record** | 违规记录，绑定 Principal-DID，跨 Agent 注销持久化。 |

---

## 2. 分层架构

```
┌──────────────────────────────────────────────────────────┐
│  L5  Application       业务 Agent (LangGraph / CrewAI…) │
├──────────────────────────────────────────────────────────┤
│  L4  Communication     Google A2A v1.0 (Agent Card,JSON-RPC)│
├──────────────────────────────────────────────────────────┤
│  L3  Trust Handshake   Agent-Score 握手扩展 (本规范核心)│
├──────────────────────────────────────────────────────────┤
│  L2  Credit Engine     评分模型 + VC 签发 (链下)        │
├──────────────────────────────────────────────────────────┤
│  L1  Registries        Identity / Reputation / Validation│
│                        / Stake / Violation (兼容 ERC-8004)│
├──────────────────────────────────────────────────────────┤
│  L0  Settlement        EVM L2 (Base / OP / Arbitrum)    │
└──────────────────────────────────────────────────────────┘
```

---

## 3. 身份层 (L1 Identity)

### 3.1 DID Method
**直接复用 `did:ethr:`**（不自定义 method），降低生态接入摩擦，钱包/解析器/工具链现成：

```
did:ethr:<chain-id>:<agent-eoa-or-erc4337-address>
example: did:ethr:0x2105:0x8004A169FB4a3325136EB29fA0ceB6D2e539a432
                  └── Base Mainnet (8453 = 0x2105)
```

`agentId` (ERC-8004 Identity Registry 的 ERC-721 tokenId) 与 DID 通过 `IdentityRegistry.didOf(agentId)` 双向解析。

### 3.2 Agent Passport (ERC-8004 兼容)
Soulbound ERC-721，metadata 锚定到 Arweave/IPFS。Agent Card 增加扩展字段：

```jsonc
{
  // —— A2A 标准字段 ——
  "name": "trade-router-agent",
  "version": "1.2.0",
  "endpoints": { "a2a": "https://agent.example.com/a2a" },
  "skills": ["routing", "risk-check"],

  // —— Agent-Score 扩展 ——
  "x-agent-score": {
    "did": "did:ethr:0x2105:0x...",
    "principal": "did:web:acme.com",         // 上级责任主体
    "operator":  "did:web:ops.acme.com",
    "stakes": [                               // 多资产质押
      { "asset": "0xA0b8...USDC", "amount": "1000000000", "lock_until": 1780000000 },
      { "asset": "native",          "amount": "500000000000000000", "lock_until": 1780000000 }
    ],
    "credit_vc": "ipfs://Qm.../credit.jwt",   // 30 天有效期 JWT-VC
    "capability_vcs": ["ipfs://Qm.../cap1.jwt"],
    "credit_authority": "did:ethr:0x2105:0xCA...",  // 必须在白名单 Registry
    "policy_uri": "ipfs://Qm.../policy.json"  // Agent 自身的拒绝策略
  }
}
```

---

## 4. 信用层 (L2 Credit Engine)

### 4.1 评分公式

```
CreditScore = clamp(0, 1000,
    300                              // 基础分
  + w_b · BehaviorScore               // 历史行为 (35%)
  + w_e · EndorsementScore            // 跨域背书 (15%)
  + w_s · StakeScore                  // 质押权重 (20%)
  + w_v · ValidationScore             // 第三方验证 (15%)
  + w_p · PrincipalScore              // 担保人信用 (15%)
  - λ  · ViolationPenalty             // 违规扣分 (含时间衰减)
)

默认权重: w_b=350, w_e=150, w_s=200, w_v=150, w_p=150, λ=400
```

### 4.2 各维度计算

**BehaviorScore**：基于近 N 次 IPR
```
BehaviorScore = (success_rate · 0.6 + on_time_rate · 0.3 + repeat_client_rate · 0.1) · 100
其中 IPR 必须由 caller 与 callee 双签 (防自吹)
```

**EndorsementScore**：背书图 PageRank + 多样性惩罚
```
EndorsementScore = PageRank(G_endorse) · DiversityFactor
DiversityFactor = 1 - max(JaccardSim(endorser_clusters))   // 防互相吹捧集群
```

**StakeScore**：多资产折算 USD 后对数缩放
```
stake_usd = Σ amount_i · price_i(oracle) · weight_i      // 每种资产可单独配权重
StakeScore = min(100, log10(stake_usd / 100) · 25)
约束: 单一资产折算占比 > 80% 时，超出部分权重折半（防单点资产风险）
```

**ValidationScore**：zkML / TEE / re-execution 验证次数与通过率。

**PrincipalScore**：上级 DID 信用分按 0.3 系数透传。

**ViolationPenalty**：违规事件 v_i 严重度（0–100 连续值）× 时间衰减
```
ViolationPenalty = Σ severity(v_i) · exp(-(t_now - t_i) / τ)   // severity ∈ [0,100]
τ = 180 天

严重度分桶（仅用于人类可读的 tier 展示，不参与公式）：
  INFO     0–20    日志/提示级，不扣 tier
  MINOR    21–40   单次小违规，可恢复
  MAJOR    41–70   降一档 tier，触发 stake 部分 slash
  CRITICAL 71–100  Principal 标黑，跨 agent 持久化，stake 全 slash
```

### 4.3 Credit VC 数据结构 (W3C VC 2.0)

```jsonc
{
  "@context": ["https://www.w3.org/ns/credentials/v2", "https://agent-score.org/v1"],
  "type": ["VerifiableCredential", "AgentCreditCredential"],
  "issuer": "did:ethr:0x2105:0xCA...",          // 必须在 CreditAuthorityRegistry 白名单
  "validFrom":  "2026-05-27T00:00:00Z",
  "validUntil": "2026-06-26T00:00:00Z",         // 固定 30 天，过期强制拒绝
  "credentialSubject": {
    "id": "did:ethr:0x2105:0x...",
    "score": 782,
    "tier":  "A",                 // S/A/B/C/D
    "dimensions": {
      "behavior": 88, "endorsement": 65, "stake": 92,
      "validation": 70, "principal": 80
    },
    "snapshot_root": "0xabc...",  // 链下 IPR Merkle Root
    "violation_count_90d": 0
  },
  "proof": { /* JWS / EIP-712 / BBS+ for ZK */ }
}
```

### 4.4 ZK 选择性披露
使用 BBS+ 签名，调用方只验：`score >= threshold` 而不暴露具体分。
电路接口：`ICircuitVerifier`（兼容 ACTA）。

---

## 5. 快速认证层 (L3 Trust Handshake)

### 5.1 握手流程（A2A 调用前置）

```
Caller(C)                                       Callee(S)
   │                                                │
   │── 1. GET /agent-card (A2A 标准) ──────────────▶│
   │◀── 2. AgentCard + x-agent-score 扩展 ──────────│
   │                                                │
   │── 3. AuthInit { nonce, caller_did, caller_vc} ▶│
   │                                                │  ① 验证 caller_did 签名
   │                                                │  ② 验证 caller credit_vc
   │                                                │     · issuer 在白名单
   │                                                │     · 未过期 & 未撤销
   │                                                │     · score >= S.policy.min_score
   │                                                │  ③ 检查 violation_count_90d
   │◀── 4. AuthAck { session_token, S.credit_vc } ──│
   │                                                │
   │── 5. Encrypted A2A JSON-RPC calls ────────────▶│
   │                                                │
   │── 6. Settle: 双签 IPR ─────────────────────────│
   │     上链: hash(IPR) → ReputationRegistry      │
```

### 5.2 性能预算
- 步骤 2–4：**< 100ms** (链下校验 + 缓存)
- 链上写入仅在步骤 6 / 周期性快照 / 纠纷裁决

### 5.3 拒绝策略 (policy.json 示例)
```jsonc
{
  "min_credit_score": 600,
  "min_tier": "B",
  "require_principal_did": true,
  "blocked_principals": ["did:web:bad.example.com"],
  "max_violation_90d": 2,
  "require_capability_vcs": ["finance.read"],
  "allow_anonymous_zk": true   // 允许 ZK 阈值证明
}
```

---

## 6. 注册表合约 (L1, ERC-8004 兼容)

| 合约 | ERC-8004 对应 | 扩展 |
|---|---|---|
| `IdentityRegistry` | ✅ ERC-8004 Identity | 增加 `principalOf(agentId)` / `didOf(agentId)` |
| `ReputationRegistry` | ✅ ERC-8004 Reputation | 增加 `submitIPR(callerSig, calleeSig, root)` |
| `ValidationRegistry` | ✅ ERC-8004 Validation | 兼容 zkML / TEE attestation |
| `StakeRegistry` | 🆕 | **多资产**: `stake(agentId, asset, amount, lockUntil)` / `slash(agentId, asset, ratio, reason)`，支持任意 ERC-20 + 原生 ETH，Chainlink/Pyth 折算 USD |
| `ViolationRegistry` | 🆕 | 绑定 **principalDID**，跨 agent 注销持久化，severity ∈ [0,100] |
| `CreditAuthorityRegistry` | 🆕 | **白名单制**：多签 admin `addAuthority/removeAuthority`，Authority 签发的 VC 才被 L3 握手承认 |

事件：
```solidity
event IPRSubmitted(uint256 indexed agentId, bytes32 root, address caller);
event Staked(uint256 indexed agentId, address asset, uint256 amount, uint64 lockUntil);
event Slashed(uint256 indexed agentId, address principal, address asset, uint256 amount, bytes32 reason);
event ViolationRecorded(address indexed principal, uint8 severity, string evidenceURI); // severity 0-100
event AuthorityAdded(address indexed authority, string metadataURI);
event AuthorityRemoved(address indexed authority, bytes32 reason);
```

---

## 7. Sybil 抵抗（双轨制）

调用方 policy 可要求**至少满足其一**：

- **Track A — Stake**: agent 锁仓 ≥ 阈值，违规 slash。适合开放/匿名场景。
- **Track B — Principal-DID 担保**: Principal 用真实身份 VC（KYB/KYC）背书，违规记录绑定 Principal 持久化。适合 B2B / 金融。

额外硬性约束：
- 同一 Principal 下 Agent 共享黑名单。
- 背书图做 Jaccard 集群检测，相似度 > 0.7 的背书权重折半。

---

## 8. 经济激励闭环

```
A2A 调用 → x402 / ERC-8183 支付 → Settlement 事件
   ↓                                    ↓
ReputationRegistry  ←  Credit Engine  ←  StakeRegistry
   ↓
新 CreditVC (30 天周期 / 触发式重算)
```

- 高信用 Agent → 更高调用价（市场定价）。
- 低信用 / 违规 → slash + tier 降级 + Principal 关联惩罚。

---

## 9. 互操作性

- **ERC-8004**: 完全兼容，`agentId` 直接复用。
- **Google A2A v1.0**: 通过 `x-agent-score` Agent Card 扩展字段，未识别的客户端忽略，向后兼容。
- **MCP**: agent 也可作为 MCP server，鉴权阶段调用本协议握手。
- **MolTrust IPR / qntm Authority**: 通过 conformance.md 测试向量验证互通。

---

## 10. 路线图

| 阶段 | 目标 | 产出 |
|---|---|---|
| M0 | 协议规范 | 本文档 + JSON Schema |
| M1 | 合约骨架 | ERC-8004 兼容 + Stake/Violation Registry |
| M2 | Credit Engine | FastAPI + LangGraph 评分流水线 |
| M3 | A2A 中间件 | Python/TS SDK，握手扩展 |
| M4 | ZK 隐私层 | BBS+ VC + 阈值证明电路 |
| M5 | 测试网 + 互操作 | Base Sepolia 部署 + ERC-8004 互通测试 |

---

## 11. 已决议事项 (2026-05-27)

- [x] **DID Method**: 直接复用 `did:ethr:`（不自定义 `did:as:`），降低生态接入摩擦，钱包/解析器现成。
- [x] **Credit Authority 准入**: M1 阶段采用 **白名单制**（多签 admin 维护 `CreditAuthorityRegistry`），后续可平滑迁移到多签 DAO。
- [x] **StakeRegistry 资产**: 支持 **多资产**（任意 ERC-20 + 原生 ETH），通过 Chainlink/Pyth 价格预言机折算为 USD 计算 `StakeScore`，每种资产可单独配置权重与最低门槛。
- [x] **CreditVC 有效期**: **30 天固定**，到期需 Credit Authority 重新签发；过期 VC 在 L3 握手强制拒绝。
- [x] **违规 Severity 量表**: **0–100 连续值**，给细粒度建模留余地；推荐分桶 `INFO 0–20 / MINOR 21–40 / MAJOR 41–70 / CRITICAL 71–100`。

---

## 12. 信用分体系落地计划 (M2)

M2 不把评分计算放到链上，而是实现一个可解释、确定性、可复算的链下 Credit Engine。链上 Registry 只提供可信数据源与锚点，Credit Authority 根据快照结果签发 30 天 CreditVC。

### 12.1 输入数据

| 输入 | 来源 | 用途 |
|---|---|---|
| `InteractionProofRecord` | `ReputationRegistry.IPRSubmitted` + 链下 IPR 批次 | 计算成功率、准时率、重复客户率、双签覆盖率 |
| `StakeSnapshot` | `StakeRegistry.positionOf` + oracle price | 计算多资产折算 USD、资产集中度、锁定期 |
| `ViolationEvent` | `ViolationRegistry.ViolationRecorded` | 计算 90 天违规数、severity 衰减惩罚、Principal 黑名单 |
| `EndorsementEdge` | 链下背书 VC / 后续 EndorsementRegistry | 计算 PageRank-like 背书与 Jaccard 集群风险 |
| `ValidationAttestation` | `ValidationRegistry.ValidationSubmitted` | 计算 zkML / TEE / re-execution 验证覆盖率 |
| `PrincipalProfile` | Principal DID / KYB/KYC VC | 计算担保方信用透传 |

### 12.2 评分流水线

```
fetch_chain_events
  → load_offchain_batches
  → normalize_features
  → detect_fraud_signals
  → calculate_dimension_scores
  → calculate_credit_score
  → assign_tier
  → emit_reason_codes
  → sign_credit_vc
```

### 12.3 第一版规则模型

- **BehaviorScore (35%)**: `success_rate 60% + on_time_rate 30% + repeat_client_rate 10%`，低样本量使用 Bayesian smoothing，避免新 agent 分数剧烈波动。
- **StakeScore (20%)**: 多资产折算 USD 后对数缩放；单一资产占比超过 80% 的超出部分权重折半。
- **EndorsementScore (15%)**: 背书图 PageRank-like 分数乘以 `DiversityFactor`；Jaccard 相似度 > 0.7 的集群权重折半。
- **ValidationScore (15%)**: 按验证类型加权，TEE < re-execution < zkML；重复 validator 只计一次。
- **PrincipalScore (15%)**: Principal 分数按 0.3 系数透传；Principal 黑名单时 agent 最高 tier 限制为 C。
- **ViolationPenalty**: severity 0–100 按 180 天指数衰减；CRITICAL 直接触发 `principal_flagged=true`。

### 12.4 分数等级

| Tier | Score | 默认策略 |
|---|---:|---|
| S | 900–1000 | 可接高风险 / 高价值 A2A 任务 |
| A | 750–899 | 默认可信，允许金融读写类能力 |
| B | 600–749 | 普通可信，适合多数工具调用 |
| C | 400–599 | 受限可信，需要额外 Principal 担保或更高 stake |
| D | 0–399 | 默认拒绝，只允许低风险查询 |

### 12.5 Reason Codes

评分结果必须输出可解释原因，便于像银行征信一样审计：

```
LOW_SAMPLE_SIZE
LOW_STAKE_USD
HIGH_STAKE_CONCENTRATION
HIGH_VIOLATION_90D
CRITICAL_PRINCIPAL_VIOLATION
ENDORSEMENT_CLUSTER_RISK
LOW_VALIDATION_COVERAGE
EXPIRED_PRINCIPAL_VC
```

### 12.6 M2 交付物

- `credit-engine/agent_score_engine/`: 纯 Python deterministic scoring library。
- `credit-engine/api/`: FastAPI 包装层，提供 `/score/{agent_id}` 与 `/issue-vc`。
- `credit-engine/schemas/`: IPR、StakeSnapshot、ViolationEvent、CreditVC JSON Schema。
- `a2a-middleware/`: 在握手阶段校验 CreditVC、issuer 白名单、分数阈值与 policy。

---

## 13. MVP Demo (本地闭环)

MVP demo 采用单进程 CLI 模式，不依赖真实 EVM 节点或多服务部署。它用于验证协议最小闭环，后续再将本地内存状态替换为 M1 Registry 合约事件和链上查询。

### 13.1 覆盖范围

```
Provider Agent 初始信用输入
  → Credit Engine 计算分数
  → Credit Authority 签发 30 天 CreditVC
  → Provider 暴露 Agent Card + x-agent-score
  → Client 校验 issuer 白名单、签名、过期时间、最低分、最低 tier
  → Client 发起 A2A 风格任务
  → Provider 返回任务结果
  → 双方生成双签 IPR
  → Provider 追加 IPR 样本
  → Credit Engine 刷新信用分
```

### 13.2 运行方式

```bash
cd /Users/bytedance/code/agent-score
PYTHONPATH=credit-engine:mvp-demo python3 mvp-demo/demo.py
```

### 13.3 验收输出

Demo 必须输出以下 5 段：

- `Provider Agent Card`: A2A card + `x-agent-score` 扩展 + 签名 CreditVC。
- `A2A Trust Handshake`: 是否通过 policy，包含 provider score / tier。
- `A2A Task Result`: 一次模拟任务调用结果。
- `Dual-Signed IPR`: IPR hash、caller signature、callee signature。
- `Score Refresh`: 调用前后分数与 tier 变化。

### 13.4 测试方式

```bash
cd /Users/bytedance/code/agent-score
PYTHONPATH=credit-engine:mvp-demo python3 -m unittest discover -s mvp-demo/tests -v
```

测试覆盖：

- 合法 provider 通过握手。
- 非白名单 issuer 被拒绝。
- 分数 / tier 低于 policy 被拒绝。
- 完整 demo 返回 IPR hash 和刷新后的分数。

---

## 14. A2A Middleware (M3)

M3 将 MVP 中的握手逻辑抽取为可复用 Python middleware 包：`a2a-middleware/agent_score_middleware/`。该包不绑定具体 Web 框架，先作为协议 SDK 使用；后续可增加 FastAPI、A2A server、MCP server adapter。

### 14.1 模块边界

| 模块 | 责任 |
|---|---|
| `models.py` | `AgentPolicy`、`AgentCard`、`HandshakeResult`、`InteractionProofRecordEnvelope` |
| `handshake.py` | 校验 Agent Card 中的 `CreditVC`、issuer 白名单、有效期、score、tier、违规数 |
| `ipr.py` | 规范化 JSON hash 与 HMAC 签名 helper，用于 demo 中的双签 IPR |

### 14.2 调用方式

```python
from agent_score_middleware import AgentPolicy, verify_agent_card_credit

policy = AgentPolicy(
    min_credit_score=600,
    min_tier="B",
    trusted_issuers={authority_did},
)

result = verify_agent_card_credit(
    provider_card,
    policy,
    secret_by_issuer={authority_did: authority_secret},
)
```

### 14.3 与 MVP Demo 的关系

`mvp-demo` 不再拥有协议核心逻辑，只作为 middleware 的使用示例：

```
credit-engine  →  a2a-middleware  →  mvp-demo
评分/VC签发       握手/IPR/策略       本地端到端演示
```

### 14.4 测试方式

```bash
cd /Users/bytedance/code/agent-score
PYTHONPATH=credit-engine:a2a-middleware:mvp-demo python3 -m unittest discover -s a2a-middleware/tests -v
```

测试覆盖：

- 合法 Agent Card 通过握手。
- 非白名单 issuer 被拒绝。
- 分数 / tier 低于 policy 被拒绝。
- IPR hash 不受签名字段变化影响。

### 14.5 FastAPI Adapter (M3.2)

`a2a-middleware/agent_score_middleware/fastapi_adapter.py` 提供可选 HTTP adapter。核心 middleware 仍不绑定 Web 框架；FastAPI adapter 只是协议示例和集成样板。

#### `GET /agent-card`

返回 provider 的 A2A Agent Card：

```jsonc
{
  "name": "provider",
  "version": "0.1.0",
  "endpoints": { "a2a": "local://provider/a2a" },
  "skills": ["risk-check"],
  "x-agent-score": {
    "did": "did:ethr:0x2105:0x...",
    "principal": "did:web:provider.example",
    "credit_vc": { "...": "AgentCreditCredential" },
    "credit_authority": "did:ethr:0x2105:0xissuer"
  }
}
```

---

## 15. Full MVP Hardening

本阶段将 MVP 从 HMAC 演示升级为更接近生产的协议雏形：`CreditVC` 支持 ES256K/JWS，HTTP A2A 调用支持 issuer 公钥验证，任务完成后可生成 IPR anchor receipt。

### 15.1 CreditVC JWS Proof

`credit-engine/agent_score_engine/jws.py` 提供 secp256k1 ES256K JWS helper。`CreditVC` 支持两种 proof：

| Proof | 用途 | 状态 |
|---|---|---|
| `AgentScoreHMAC2026` | 本地测试、兼容旧 demo | 保留 |
| `AgentScoreJWS2026` | 生产雏形，issuer 私钥签名、公钥验证 | 推荐 |

JWS proof 示例：

```jsonc
{
  "proof": {
    "type": "AgentScoreJWS2026",
    "created": "2026-05-27T12:00:00Z",
    "verificationMethod": "did:ethr:0x2105:0x...",
    "proofPurpose": "assertionMethod",
    "jws": "base64url(header).base64url(payload).base64url(signature)"
  }
}
```

验证规则：

- issuer 必须在 `trusted_issuers` 白名单内。
- `validFrom <= now < validUntil`。
- JWS payload 必须等于去除 `proof` 后的 VC canonical payload。
- 签名必须通过 `public_key_by_issuer[issuer]` 验证。

### 15.2 IPR Anchor

`a2a-middleware/agent_score_middleware/anchors.py` 定义 IPR 锚定抽象。当前实现为 `InMemoryIPRAnchor`，用于本地验证；生产实现可替换为 `ReputationRegistry.submitInteractionRoot()` 或 L2 事件锚定。

Anchor receipt：

```jsonc
{
  "anchor_type": "in_memory_reputation_registry",
  "ipr_hash": "64-char sha256",
  "anchor_id": "ipr-anchor-1",
  "created_at": "2026-05-27T12:00:00Z"
}
```

### 15.3 HTTP 双 Agent Demo

`http-demo/demo.py` 使用 FastAPI `TestClient` 模拟真实 HTTP A2A：

```
Credit Authority ES256K keypair
  → caller/provider 生成 JWS CreditVC
  → provider FastAPI app 暴露 /agent-card 和 /a2a
  → caller POST /a2a
  → provider 校验 caller CreditVC JWS
  → task_handler 执行任务
  → 生成 IPR
  → InMemoryIPRAnchor 返回 anchor receipt
```

运行方式：

```bash
cd /Users/bytedance/code/agent-score
PYTHONPATH=credit-engine:a2a-middleware:mvp-demo:http-demo python3 http-demo/demo.py
```

### 15.4 全量验证

```bash
cd /Users/bytedance/code/agent-score
PYTHONPATH=credit-engine:a2a-middleware:mvp-demo:http-demo python3 -m unittest discover -s credit-engine/tests -v
PYTHONPATH=credit-engine:a2a-middleware:mvp-demo:http-demo python3 -m unittest discover -s a2a-middleware/tests -v
PYTHONPATH=credit-engine:a2a-middleware:mvp-demo:http-demo python3 -m unittest discover -s mvp-demo/tests -v
PYTHONPATH=credit-engine:a2a-middleware:mvp-demo:http-demo python3 -m unittest discover -s http-demo/tests -v
```

#### `POST /a2a`

请求体：

```jsonc
{
  "caller_card": {
    "name": "caller",
    "version": "0.1.0",
    "endpoint": "local://caller/a2a",
    "skills": ["task.request"],
    "did": "did:ethr:0x2105:0xcaller",
    "principal": "did:web:caller.example",
    "credit_vc": { "...": "AgentCreditCredential" }
  },
  "task": {
    "task_id": "task-1",
    "prompt": "run risk check"
  }
}
```

处理逻辑：

```
caller_card → verify_agent_card_credit(policy)
  → accepted: task_handler(task) → result + dual-signed IPR
  → rejected: HTTP 403 { detail: { reason } }
```

响应体：

```jsonc
{
  "handshake": {
    "accepted": true,
    "reason": "ACCEPTED",
    "provider_score": 780,
    "provider_tier": "A"
  },
  "result": {
    "task_id": "task-1",
    "status": "completed",
    "answer": "handled run risk check"
  },
  "ipr": {
    "hash": "64-char sha256",
    "caller_signature": "caller signature",
    "callee_signature": "provider signature"
  }
}
```

---

## 16. 设备与网络绑定 (Device & Network Binding)

### 16.1 动机与目标

Agent 的 DID 身份（"身份证"）只能证明其关联的 Principal，但无法防止密钥被盗用或 Agent 被迁移到未授权设备运行。本章节通过**设备硬件绑定**和**网络指纹绑定**，确保 Agent 身份与物理运行环境强关联，实现"Agent → 设备 → 主人"的完整信任链。

**核心目标**：
- 防止 Agent 私钥被盗后在其他设备滥用
- 检测异常网络位置漂移（如密钥泄露后在异地登录）
- 在设备绑定降级时要求 Principal 二次确认
- 将设备可信度纳入信用评分体系

### 16.2 绑定级别 (BindingLevel)

| 级别 | 含义 | 场景 | 设备得分 |
|---|---|---|---|
| `none` | 无任何设备绑定 | 纯云端无状态 Agent、测试环境 | 0 |
| `registration` | 注册时绑定设备硬件指纹 | 首次部署时记录设备信息 | 50 |
| `runtime` | 运行时持续验证设备状态 | TEE/TPM 定期 attestation | 75 |
| `strong` | 强绑定：TEE + 运行时验证 + Principal 签名 | 高安全场景（金融、身份） | 100 |

### 16.3 数据模型

#### DeviceAttestation（设备证明）

由 TEE/TPM 或设备权威机构签发的硬件证明：

```jsonc
{
  "attestation_type": "tpm_quote" | "tee_report" | "secure_enclave" | "mock",
  "device_id": "uuid-or-tpm-pubkey-hash",
  "hardware_model": "MacBookPro18,3",
  "tee_type": "SGX" | "SEV" | "TrustZone" | "AppleSE" | null,
  "quote": "base64-encoded-tpm-quote-or-tee-report",
  "signature": "base64-encoded-device-signature",
  "timestamp": "2026-05-28T10:00:00Z"
}
```

#### NetworkFingerprint（网络指纹）

运行时网络环境特征，用于漂移检测：

```jsonc
{
  "ip_prefix": "203.0.113.0/24",      // 保留前缀，不存完整 IP
  "asn": 12345,                       // 自治系统号
  "country_code": "SG",               // ISO 3166-1 alpha-2
  "city_geo_hash": "w21z7",           // 城市级 geohash
  "timestamp": "2026-05-28T10:00:00Z"
}
```

#### DeviceProfile（设备画像）

Agent Card 扩展字段，聚合设备与网络信息：

```jsonc
{
  "binding_level": "strong",
  "attestation": { /* DeviceAttestation */ },
  "network": { /* NetworkFingerprint */ },
  "registered_country_code": "SG",    // 注册时国家
  "registered_asn": 12345,            // 注册时 ASN
  "has_network_drift": false,         // 当前网络与注册网络是否漂移
  "has_principal_co_sign": false      // 漂移时是否有 Principal 副署
}
```

### 16.4 DeviceBindingVC（设备绑定凭证）

由 Device Authority（设备权威机构）签发的 W3C VC，有效期 **24 小时**（短有效期确保持续验证）：

```jsonc
{
  "@context": ["https://www.w3.org/ns/credentials/v2", "https://agent-score.org/v1"],
  "type": ["VerifiableCredential", "DeviceBindingCredential"],
  "issuer": "did:ethr:0x2105:0xDEVICE_AUTHORITY",
  "issuanceDate": "2026-05-28T10:00:00Z",
  "expirationDate": "2026-05-29T10:00:00Z",   // 24 小时有效期
  "credentialSubject": {
    "id": "did:ethr:0x2105:0xAGENT",
    "principal": "did:web:owner.example",
    "device_id": "device-uuid-12345",
    "binding_level": "strong",
    "attestation_type": "tpm_quote",
    "registered_country_code": "SG",
    "registered_asn": 12345,
    "hardware_model": "MacBookPro18,3"
  },
  "proof": {
    "type": "AgentScoreJWS2026",
    "created": "2026-05-28T10:00:00Z",
    "verificationMethod": "did:ethr:0x2105:0xDEVICE_AUTHORITY",
    "proofPurpose": "assertionMethod",
    "jws": "base64url(header).base64url(payload).base64url(signature)"
  }
}
```

### 16.5 信用评分扩展

#### 评分公式调整

新增 `DeviceScore` 维度，权重 **10%**（100 分），`PrincipalScore` 权重从 15% 调整为 5%：

```
CreditScore = clamp(0, 1000,
    300                              // 基础分
  + w_b · BehaviorScore               // 历史行为 (35%, 350 分)
  + w_e · EndorsementScore            // 跨域背书 (15%, 150 分)
  + w_s · StakeScore                  // 质押权重 (20%, 200 分)
  + w_v · ValidationScore             // 第三方验证 (15%, 150 分)
  + w_d · DeviceScore                 // 设备绑定 (10%, 100 分)  ← 新增
  + w_p · PrincipalScore              // 担保人信用 (5%, 50 分)   ← 调整
  - λ  · ViolationPenalty             // 违规扣分
)
```

#### DeviceScore 计算规则

```python
DeviceScore = level_scores[binding_level]
if has_network_drift and not has_principal_co_sign:
    DeviceScore = max(0, DeviceScore - 50)  # 漂移且无副署，扣 50 分
```

#### Reason Codes 扩展

| Code | 含义 |
|---|---|
| `NO_DEVICE_BINDING` | Agent 无任何设备绑定 |
| `NETWORK_DRIFT_WITHOUT_PRINCIPAL_COSIGN` | 网络漂移且无 Principal 副署 |

### 16.6 握手协议扩展

#### Agent Card 扩展字段

Agent Card 新增设备绑定相关字段：

```jsonc
{
  "name": "trade-router-agent",
  "version": "1.2.0",
  "x-agent-score": {
    "did": "did:ethr:0x2105:0x...",
    "principal": "did:web:acme.com",
    "credit_vc": { /* ... */ },
    "device_binding_vc": { /* DeviceBindingVC */ },   // ← 新增
    "network_fingerprint": { /* NetworkFingerprint */ }  // ← 新增
  }
}
```

#### AgentPolicy 扩展字段

调用方可通过 policy 配置设备绑定要求：

```python
@dataclass
class AgentPolicy:
    # ... 原有字段 ...
    require_device_binding: bool = False
    min_binding_level: str = "registration"
    trusted_device_authorities: Set[str] = field(default_factory=set)
    allowed_countries: Set[str] = field(default_factory=set)
    blocked_asns: Set[int] = field(default_factory=set)
    require_principal_co_sign_on_drift: bool = True
```

#### 设备绑定校验流程

握手阶段新增设备绑定校验分支（`_verify_device_binding`）：

```
1. 若 policy.require_device_binding = false，跳过校验
2. 检查 device_binding_vc 是否存在 → 缺失返回 MISSING_DEVICE_BINDING
3. 验证 issuer 是否在 trusted_device_authorities → 不在返回 UNTRUSTED_DEVICE_AUTHORITY
4. 验证 VC 有效期（24 小时）→ 过期返回 EXPIRED_DEVICE_BINDING
5. 验证 JWS 签名（alg=ES256K, kid=issuer）→ 失败返回 INVALID_DEVICE_BINDING
6. 检查 binding_level >= min_binding_level → 不满足返回 INSUFFICIENT_BINDING_LEVEL
7. 检查 country_code 是否在 allowed_countries → 不在返回 COUNTRY_NOT_ALLOWED
8. 检查 asn 是否在 blocked_asns → 在返回 ASN_BLOCKED
9. 检测网络漂移（country/asn 与注册时不同）
   → 若漂移且 require_principal_co_sign_on_drift 且无副署
     → 返回 NETWORK_DRIFT_WITHOUT_PRINCIPAL_COSIGN
10. 全部通过 → None（校验成功）
```

### 16.7 网络漂移检测与处理

**漂移判定条件**（满足任一即视为漂移）：
- `current.country_code != registered_country_code`
- `current.asn != registered_asn`

**漂移处理策略**：

| 场景 | 策略 |
|---|---|
| 首次注册 | 记录 `registered_country_code` 和 `registered_asn` 作为基线 |
| 漂移 + Principal 副署 | 允许访问，不扣分（视为合法迁移） |
| 漂移 + 无副署 | 拒绝访问，扣 50 分 DeviceScore |
| 持续漂移 > 7 天 | 触发 Principal 告警，建议重新绑定 |

**Principal 副署格式**：
Agent 发起请求时，在 `caller_signature` 字段同时包含 Agent 签名和 Principal 签名（双签），或在 `x-agent-score` 扩展中增加 `principal_signature` 字段。

### 16.8 安全考虑

1. **JWS 头部校验**：验证 `alg=ES256K` 且 `kid=issuer`，防止算法降级攻击。
2. **短有效期**：DeviceBindingVC 有效期 24 小时，确保持续验证。
3. **隐私保护**：只存 IP 前缀（/24）和 geohash，不存完整 IP 地址。
4. **防篡改**：设备证明由 TEE/TPM 硬件签名，不可伪造。
5. **可选启用**：设备绑定通过 policy 开关控制，不影响现有无绑定场景。

### 16.9 实现状态

- ✅ 数据模型：`DeviceAttestation`、`NetworkFingerprint`、`DeviceProfile`
- ✅ 评分扩展：`DeviceScore` 维度 + 漂移扣分逻辑
- ✅ VC 签发与验证：`DeviceBindingVC` JWS 签名与校验
- ✅ 握手扩展：`_verify_device_binding` 校验流程
- ✅ Policy 扩展：设备绑定相关策略字段
- ✅ 测试覆盖：强绑定通过、缺失拒绝、漂移无副署拒绝、漂移有副署通过
- ⏳ TEE/TPM 集成：当前为 mock attestation，后续可接入真实硬件
- ⏳ IP/ASN/Geo 数据库：当前为 mock 数据，后续可接入 MaxMind/IP2Location
