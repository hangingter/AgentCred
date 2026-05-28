# Minimal Agent Demo

最小化的 Agent-Score 协议演示，帮助你快速理解如何使用协议声明 Agent 身份和进行可信交易。

## 两个核心场景

### 1. 声明 Agent 身份 (`1_declare_agent.py`)

展示如何将你的本地 Agent 接入协议，获得"身份证"：

```
Step 1: 定义 Agent 基本信息 (DID, Principal, 技能等)
Step 2: 积累 Agent 信用数据 (历史交互、质押、背书等)
Step 3: 计算信用分和等级
Step 4: 由 Credit Authority 签发 CreditVC
Step 5: 生成 Agent Card (对外名片)
```

**运行命令：**
```bash
cd /Users/bytedance/code/agent-score
PYTHONPATH=credit-engine:a2a-middleware:mvp-demo:minimal-demo python3 minimal-demo/1_declare_agent.py
```

### 2. 双方可信交易 (`2_trade_with_protocol.py`)

展示两个 Agent 如何利用协议进行完整的可信交易：

```
Step 1: 买卖双方初始化并声明身份
Step 2: 买方设置交易策略 (信任门槛)
Step 3: 握手 - 买方验证卖方信用
Step 4: 交易 - 执行任务
Step 5: 存证 - 生成双签 IPR 记录
Step 6: 结算 - 更新双方信用分
```

**运行命令：**
```bash
cd /Users/bytedance/code/agent-score
PYTHONPATH=credit-engine:a2a-middleware:mvp-demo:minimal-demo python3 minimal-demo/2_trade_with_protocol.py
```

## 核心概念速查

| 概念 | 说明 | 代码位置 |
|---|---|---|
| **DID** | Agent 的去中心化身份 | `did:ethr:<chain>:<address>` |
| **Principal** | Agent 背后的责任主体 (人/组织) | `did:web:example.com` |
| **CreditVC** | 信用凭证，由权威机构签发 | `build_credit_vc()` + `sign_credit_vc()` |
| **Agent Card** | Agent 对外名片，包含 CreditVC | `AgentCard` 类 |
| **AgentPolicy** | 交易方的信任门槛策略 | `AgentPolicy` 类 |
| **Handshake** | 握手验证，检查对方信用 | `verify_agent_card_credit()` |
| **IPR** | 交互证明记录，双签防抵赖 | `InteractionProofRecordEnvelope` |
| **DeviceBinding** | 设备绑定，防止密钥盗用 | `DeviceProfile` + `DeviceBindingVC` |

## 如何将你的 Agent 接入协议

### 最小接入代码

```python
from agent_score_engine import CreditInput, calculate_credit_score, build_credit_vc, sign_credit_vc
from agent_score_middleware import AgentCard

# 1. 准备你的 Agent 信用数据
credit_input = CreditInput(
    agent_id="did:ethr:0x2105:0x...",
    interactions=[...],  # 历史交互记录
    stakes=[...],        # 质押资产
    validations=[...],   # 第三方验证
    principal=PrincipalProfile(score=800),
)

# 2. 计算信用分
score = calculate_credit_score(credit_input)

# 3. 由 Credit Authority 签发 CreditVC
vc = build_credit_vc(score, issuer=AUTHORITY_DID, ...)
signed_vc = sign_credit_vc(vc, issuer=AUTHORITY_DID, secret=AUTHORITY_SECRET, ...)

# 4. 生成 Agent Card 对外发布
card = AgentCard(
    name="my-agent",
    version="1.0.0",
    endpoint="https://my-agent.com/a2a",
    skills=["trade.execute"],
    did="did:ethr:0x2105:0x...",
    principal="did:web:my-company.com",
    credit_vc=signed_vc,
)

# 5. 在你的 Agent 端点暴露 GET /agent-card 返回 card.to_a2a_dict()
```

### 作为调用方验证对方

```python
from agent_score_middleware import AgentPolicy, verify_agent_card_credit

# 设置你的信任门槛
policy = AgentPolicy(
    min_credit_score=600,
    min_tier="B",
    trusted_issuers={AUTHORITY_DID},
    require_device_binding=True,
)

# 验证对方 Agent Card
result = verify_agent_card_credit(
    other_agent_card,
    policy,
    secret_by_issuer={AUTHORITY_DID: AUTHORITY_SECRET},
)

if result.accepted:
    print(f"✅ 可信！对方分数: {result.score}, 等级: {result.tier}")
else:
    print(f"❌ 不可信！原因: {result.reason}")
```

## 安全保障

1. **身份防伪造**：DID + JWS 签名，CreditVC 不可篡改
2. **算法防降级**：强制 `alg=ES256K` + `kid=issuer` 校验
3. **密钥防盗用**：设备绑定 + 网络漂移检测
4. **交易防抵赖**：IPR 双重签名，链上锚定
5. **违规可追溯**：违规记录绑定 Principal，跨 Agent 持久化
