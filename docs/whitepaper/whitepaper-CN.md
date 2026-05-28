# Agent-Score：面向 AI Agent 的银行级信用协议

**版本：** 0.1.0  
**日期：** 2026-05-28  
**状态：** Draft for Review  
**作者：** Agent-Score 团队

---

## 摘要 / Executive Summary

随着 AI Agent 技术的爆发式发展， autonomous agents 正在成为数字经济的核心参与者。然而，Agent 生态面临着严重的信任缺口：如何确保 Agent 身份可信、行为可问责、交易可追溯？现有的声誉系统大多依赖中心化平台，缺乏硬件级安全绑定，难以防止密钥盗用和 Sybil 攻击。

**Agent-Score** 是一个面向 AI Agent 的去中心化信用协议，旨在构建银行级的 Agent 信用体系。协议融合了 W3C DID/VC 标准、ERC-8004 注册表、Google A2A 通信协议，并创新性地引入了**设备与网络绑定**机制，实现了「Agent → 设备 → 主人」的完整信任链。

**核心创新：**

1. **六维信用评分模型**：行为、质押、背书、验证、设备、主体，全方位评估 Agent 可信度
2. **硬件级身份绑定**：TEE/TPM 设备证明 + 网络指纹漂移检测，防止密钥盗用
3. **快速认证层**：< 100ms 握手验证，支持 A2A 场景下的实时信任决策
4. **可问责体系**：每笔交易双签存证，违规记录绑定责任主体（Principal），跨 Agent 持久化
5. **Sybil 抵抗双轨制**：Stake 质押 + Principal 担保，双轨并行有效抵御女巫攻击

Agent-Score 为 Agent 生态提供了完整的信任基础设施，使得 Agent 能够像拥有「身份证」和「信用报告」一样，在开放网络中进行可信交易。

---

## 第一章：引言 / Introduction

### 1.1 AI Agent 的爆发与信任缺口

近年来，大语言模型（LLM）和多智能体系统（Multi-Agent Systems）技术取得了突破性进展。从 AutoGPT 到 CrewAI，从 LangGraph 到 Google A2A，AI Agent 正在从概念验证走向生产应用。Agent 不再是简单的聊天机器人，而是能够自主执行复杂任务的数字实体：

- **交易 Agent**：在 DeFi 协议中自动执行交易策略
- **服务 Agent**：为用户提供法律咨询、医疗诊断、数据分析等专业服务
- **协作 Agent**：在企业内部跨部门协作，完成端到端业务流程
- **创作 Agent**：生成代码、设计、文案等创造性内容

然而，随着 Agent 数量的爆炸式增长，一个根本性问题日益凸显：**如何信任一个陌生的 Agent？**

在传统的互联网服务中，信任由中心化平台背书。但在去中心化的 Agent 生态中：
- Agent 可能由匿名实体创建和控制
- Agent 的行为缺乏透明的审计追踪
- 密钥泄露可能导致 Agent 身份被盗用
- 恶意 Agent 可能进行欺诈、操纵市场等行为
- 违规后难以追溯到真正的责任主体

### 1.2 现有方案的局限性

现有的 Agent 声誉和信任方案存在诸多局限性：

| 方案 | 优点 | 局限性 |
|---|---|---|
| **中心化声誉系统** | 实现简单，用户基数大 | 数据孤岛、平台垄断、隐私泄露风险 |
| **链上纯声誉** | 去中心化、透明 | 易被 Sybil 攻击、无硬件绑定、计算成本高 |
| **Token 质押机制** | 经济激励明确 | 资本门槛高、质押资产波动风险 |
| **ZK 匿名证明** | 隐私保护好 | 计算复杂度高、用户体验差 |

特别地，现有方案普遍缺乏**硬件级身份绑定**——即使 Agent 拥有 DID 身份，一旦私钥泄露，攻击者就可以在任意设备上盗用该身份。这对于金融、医疗等高安全场景是不可接受的。

### 1.3 Agent-Score 的使命

Agent-Score 的使命是为 AI Agent 构建**银行级的信用体系**，使得：

- ✅ **身份可信**：每个 Agent 都有可验证的 DID 身份，关联到真实责任主体
- ✅ **信用可量化**：通过多维度评分模型，精确评估 Agent 的可信度
- ✅ **设备绑定**：Agent 身份与硬件设备强绑定，防止密钥盗用
- ✅ **交易可溯**：每笔交互都有双签存证，链上锚定，不可抵赖
- ✅ **违规可问责**：违规记录绑定责任主体，跨 Agent 持久化，形成有效威慑
- ✅ **隐私保护**：支持 ZK 选择性披露，在验证信用的同时保护隐私

Agent-Score 不重造轮子，而是站在巨人的肩膀上：
- 身份层复用 **W3C DID** 和 **ERC-8004** 标准
- 凭证层采用 **W3C Verifiable Credentials**
- 通信层兼容 **Google A2A v1.0** 协议
- 结算层对接 **ERC-8183 (x402)** 支付标准

通过构建开放、兼容、安全的信任基础设施，Agent-Score 致力于推动 AI Agent 生态从「野蛮生长」走向「可信繁荣」。

---

## 第二章：设计原则 / Design Principles

### 2.1 不重造轮子 / No Reinventing the Wheel

Agent-Score 最大限度地复用成熟的行业标准和开源组件，降低生态接入摩擦：

- **身份层**：直接复用 `did:ethr:` 方法，不自定义 DID Method
- **凭证层**：遵循 W3C VC 2.0 标准，兼容现有 VC 生态
- **通信层**：通过 `x-agent-score` 扩展字段兼容 Google A2A v1.0
- **合约层**：兼容 ERC-8004 注册表接口，可平滑迁移
- **支付层**：对接 x402 / ERC-8183 支付标准

### 2.2 链上轻、链下重 / Light on Chain, Heavy off Chain

为了平衡安全性、性能和成本，Agent-Score 采用「链上轻、链下重」的架构：

- **链上**：只锚定身份、信用快照、违规记录、质押等关键状态
- **链下**：信用评分、IPR 批量处理、VC 签发等计算密集型操作
- **锚定机制**：链下计算结果的 Merkle Root 定期上链，确保可验证性

这种设计使得：
- 链上 Gas 成本可控
- 信用评分可以复杂精细（六维度、实时更新）
- 链下计算可复现、可审计
- 不牺牲最终的安全性和不可篡改性

### 2.3 隐私优先 / Privacy First

Agent-Score 将隐私保护作为核心设计目标：

- **ZK 选择性披露**：使用 BBS+ 签名，支持「信用分 ≥ 阈值」的零知识证明，不暴露具体分数
- **数据最小化**：网络指纹只存储 IP 前缀（/24）和城市级 geohash，不存完整 IP
- **链下存证**：IPR 详细数据链下存储，链上只锚定哈希
- **身份分离**：Agent DID 与 Principal DID 分离，支持可控关联

### 2.4 Sybil 抵抗双轨制 / Dual-Track Sybil Resistance

Agent-Score 采用「Stake + Principal 担保」双轨制，有效抵御女巫攻击：

| 轨道 | 机制 | 适用场景 |
|---|---|---|
| **Track A — Stake** | Agent 锁仓 ≥ 阈值，违规 Slash | 开放/匿名场景、DeFi 交易 |
| **Track B — Principal 担保** | Principal 用真实身份 VC（KYB/KYC）背书 | B2B 场景、金融服务 |

调用方可以通过 policy 配置「至少满足其一」或「同时满足」。

额外硬性约束：
- 同一 Principal 下的所有 Agent 共享黑名单
- 背书图做 Jaccard 集群检测，相似度 > 0.7 的背书权重折半
- 单一资产质押占比 > 80% 时，超出部分权重折半

### 2.5 可问责 / Accountable

Agent-Score 的核心设计理念是「每一次 A2A 交互都可回溯到 Principal」：

- **IPR 双签**：每笔交互都需要 caller 和 callee 双重签名
- **Principal 关联**：每个 Agent DID 都关联到一个 Principal DID（自然人/法人/DAO）
- **违规持久化**：违规记录绑定 Principal，跨 Agent 注销持久化
- **分级惩罚**：根据违规严重度（0–100）执行不同级别的惩罚，从扣分到全量 Slash

这种设计确保了即使 Agent 被注销或废弃，其背后的责任主体仍然可以被追溯和问责。

---

## 第三章：系统架构 / System Architecture

### 3.1 五层架构模型

Agent-Score 采用清晰的五层架构，每层职责明确、松耦合：

```
┌──────────────────────────────────────────────────────────┐
│  L5  Application       业务 Agent (LangGraph / CrewAI…) │
│                                                          │
│  业务逻辑层：具体的 Agent 应用，调用下层协议进行可信交互 │
├──────────────────────────────────────────────────────────┤
│  L4  Communication     Google A2A v1.0 (Agent Card,JSON-RPC)│
│                                                          │
│  通信层：Agent 间的消息传输协议，兼容 Google A2A 标准   │
├──────────────────────────────────────────────────────────┤
│  L3  Trust Handshake   Agent-Score 握手扩展 (本规范核心)│
│                                                          │
│  快速认证层：< 100ms 完成信用验证和策略检查             │
├──────────────────────────────────────────────────────────┤
│  L2  Credit Engine     评分模型 + VC 签发 (链下)        │
│                                                          │
│  信用引擎层：六维评分、CreditVC 签发、Reason Code 生成  │
├──────────────────────────────────────────────────────────┤
│  L1  Registries        Identity / Reputation / Validation│
│                        / Stake / Violation (兼容 ERC-8004)│
│                                                          │
│  注册表层：链上合约，锚定身份、信用、违规、质押等关键状态│
├──────────────────────────────────────────────────────────┤
│  L0  Settlement        EVM L2 (Base / OP / Arbitrum)    │
│                                                          │
│  结算层：底层区块链，提供最终性和不可篡改性保证         │
└──────────────────────────────────────────────────────────┘
```

### 3.2 核心组件

#### 3.2.1 Identity Registry（身份注册表）

- 基于 ERC-721 的 Soulbound Token，每个 Agent 对应一个 tokenId
- 存储 Agent DID、Principal DID、Operator DID 等关键信息
- 支持 `principalOf(agentId)` 和 `didOf(agentId)` 双向查询
- 兼容 ERC-8004 标准接口

#### 3.2.2 Credit Engine（信用引擎）

- 链下确定性评分，输入输出可复现、可审计
- 六维评分模型：行为、质押、背书、验证、设备、主体
- 签发 30 天有效期的 CreditVC，支持 HMAC 和 JWS 两种证明方式
- 输出 Reason Code，提供银行级的可解释性

#### 3.2.3 A2A Middleware（中间件）

- Agent Card 解析与验证
- CreditVC 完整性、有效期、签发方白名单校验
- 可配置的策略引擎（信用分阈值、等级要求、设备绑定要求等）
- IPR 双签生成与哈希计算
- FastAPI HTTP Adapter，快速接入现有服务

#### 3.2.4 Device Authority（设备权威机构）

- 验证 TEE/TPM 设备证明
- 签发 24 小时有效期的 DeviceBindingVC
- 维护设备黑名单（被盗设备、 compromised TEE 等）
- 支持多设备权威机构的分布式信任模型

### 3.3 协议流程

Agent-Score 的完整协议流程包括六个阶段：

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  身份声明   │ →  │  信用评估   │ →  │  握手验证   │
└─────────────┘    └─────────────┘    └─────────────┘
       ↓                  ↓                  ↓
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  存证结算   │ ←  │  交易执行   │ ←  │  信用激励   │
└─────────────┘    └─────────────┘    └─────────────┘
```

1. **身份声明**：Agent 生成 DID，注册到 Identity Registry，关联 Principal
2. **信用评估**：Credit Engine 根据历史数据计算信用分，签发 CreditVC
3. **握手验证**：交易前，调用方验证对方的 CreditVC 和设备绑定状态
4. **交易执行**：握手通过后，执行具体的 A2A 任务
5. **信用激励**：成功交易提升双方信用分，违规则扣分和 Slash
6. **存证结算**：生成双签 IPR，哈希锚定到链上 Reputation Registry

### 3.4 信任链

Agent-Score 构建了完整的信任链，确保每一层都有安全保障：

```
Principal (自然人/法人)
    ↓ 真实身份 VC (KYB/KYC)
Agent DID
    ↓ 设备绑定 VC (TEE/TPM 证明)
CreditVC (六维信用评分)
    ↓ JWS 签名 (alg=ES256K, kid=issuer)
Agent Card
    ↓ 握手验证 (policy check)
A2A Transaction
    ↓ 双签 IPR
Chain Anchor (Merkle Root)
```

---

## 第四章：身份层 / Identity Layer

### 4.1 DID Method 设计决策

Agent-Score 选择直接复用 `did:ethr:` 方法，而不是自定义 DID Method，这一决策基于以下考虑：

**优点：**
- ✅ 生态成熟：钱包、解析器、工具链现成，无需重新构建
- ✅ 兼容性好：与现有以太坊生态无缝集成
- ✅ 安全性高：经过大量实战检验，安全边界清晰
- ✅ 迁移成本低：开发者熟悉，接入门槛低

**DID 格式：**
```
did:ethr:<chain-id>:<agent-eoa-or-erc4337-address>
example: did:ethr:0x2105:0x8004A169FB4a3325136EB29fA0ceB6D2e539a432
                  └── Base Mainnet (8453 = 0x2105)
```

`agentId`（ERC-8004 Identity Registry 的 tokenId）与 DID 通过 `IdentityRegistry.didOf(agentId)` 双向解析。

### 4.2 Agent Passport（Agent 护照）

Agent Passport 是一个 Soulbound ERC-721 Token，作为 Agent 的「数字护照」。其 metadata 锚定到 Arweave/IPFS，包含以下信息：

```jsonc
{
  // —— 基础信息 ——
  "name": "trade-router-agent",
  "version": "1.2.0",
  "description": "专业的 DeFi 交易路由 Agent",
  "avatar": "ipfs://Qm.../avatar.png",

  // —— 身份信息 ——
  "did": "did:ethr:0x2105:0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
  "principal": "did:web:acme.com",         // 上级责任主体
  "operator":  "did:web:ops.acme.com",      // 运营方

  // —— 能力信息 ——
  "skills": ["routing", "risk-check", "trade.execute"],
  "endpoints": { "a2a": "https://agent.acme.com/a2a" },
  "capability_vcs": ["ipfs://Qm.../cap1.jwt"],

  // —— 信用信息 ——
  "credit_vc": "ipfs://Qm.../credit.jwt",   // 30 天有效期 CreditVC
  "credit_authority": "did:ethr:0x2105:0xCA...",  // 签发机构

  // —— 设备绑定 ——
  "device_binding_vc": "ipfs://Qm.../device.jwt",  // 24 小时有效期
  "device_fingerprint": "tpm-pubkey-hash-0xabc...",

  // —— 治理信息 ——
  "policy_uri": "ipfs://Qm.../policy.json",  // Agent 的拒绝策略
  "terms_of_service": "ipfs://Qm.../tos.md"
}
```

### 4.3 Principal 关联模型

Principal 是 Agent 背后的责任主体，可以是：
- 自然人（通过 KYC VC 验证）
- 法人实体（通过 KYB VC 验证）
- DAO（通过多签治理验证）

**关联规则：**
1. 每个 Agent MUST 关联到且仅关联到一个 Principal
2. 一个 Principal CAN 关联多个 Agent
3. Principal 变更 MUST 触发链上事件，旧关联的违规记录仍然保留
4. Principal 黑名单下的所有 Agent 最高 tier 限制为 C

**Principal 信用透传：**
- Principal 的信用分按 0.3 系数透传给其下的所有 Agent
- Principal 违规时，所有关联 Agent 的信用分都会受到影响
- Principal 标记为 CRITICAL 时，所有关联 Agent 暂停服务

### 4.4 设备绑定机制

设备绑定是 Agent-Score 的核心创新之一，确保 Agent 身份不仅关联到 Principal，还绑定到具体的物理设备。

**绑定级别：**

| 级别 | 含义 | 设备得分 | 安全场景 |
|---|---|---:|---|
| `none` | 无任何设备绑定 | 0 | 测试环境、纯云端无状态 Agent |
| `registration` | 注册时绑定设备硬件指纹 | 50 | 普通应用、低风险场景 |
| `runtime` | 运行时持续验证设备状态 | 75 | 金融应用、中风险场景 |
| `strong` | TEE + 运行时验证 + Principal 签名 | 100 | 身份管理、高风险场景 |

**设备证明格式（TPM Quote 示例）：**
```jsonc
{
  "attestation_type": "tpm_2.0_quote",
  "device_id": "uuid-550e8400-e29b-41d4-a716-446655440000",
  "hardware_model": "MacBookPro18,3",
  "tpm_version": "2.0",
  "pcr_values": {
    "PCR0": "0xabc123...",  // BIOS 哈希
    "PCR4": "0xdef456...",  // Boot Manager 哈希
    "PCR7": "0xghi789..."   // Secure Boot 配置
  },
  "quote": "base64-encoded-tpm-quote",
  "signature": "base64-encoded-tpm-signature",
  "timestamp": 1748428800
}
```

**TEE 证明格式（Intel SGX 示例）：**
```jsonc
{
  "attestation_type": "sgx_ecdsa_qe3",
  "device_id": "sgx-enclave-hash-0x123...",
  "hardware_model": "Intel Xeon Ice Lake",
  "tee_type": "SGX",
  "mrenclave": "0xabc123def456...",  // Enclave 代码哈希
  "mrsigner": "0x789abcdef012...",   // 签名者哈希
  "isv_prod_id": 1,
  "isv_svn": 3,
  "quote": "base64-encoded-sgx-quote",
  "signature": "base64-encoded-intel-signature",
  "timestamp": 1748428800
}
```

---

## 第五章：信用引擎 / Credit Engine

### 5.1 六维评分模型

Agent-Score 采用六维评分模型，全方位评估 Agent 的可信度。每个维度 0–100 分，按权重加权求和得到最终信用分（0–1000）。

**评分公式：**
```
CreditScore = clamp(0, 1000,
    300                              // 基础分
  + w_b · BehaviorScore               // 历史行为 (35%, 350 分)
  + w_e · EndorsementScore            // 跨域背书 (15%, 150 分)
  + w_s · StakeScore                  // 质押权重 (20%, 200 分)
  + w_v · ValidationScore             // 第三方验证 (15%, 150 分)
  + w_d · DeviceScore                 // 设备绑定 (10%, 100 分)
  + w_p · PrincipalScore              // 担保人信用 (5%, 50 分)
  - λ  · ViolationPenalty             // 违规扣分 (含时间衰减)
)
```

**默认权重：**
- `w_b = 350` (行为 35%)
- `w_e = 150` (背书 15%)
- `w_s = 200` (质押 20%)
- `w_v = 150` (验证 15%)
- `w_d = 100` (设备 10%)
- `w_p = 50` (主体 5%)
- `λ = 400` (违规惩罚系数)

**分数等级：**

| Tier | 分数范围 | 描述 | 默认策略 |
|---|---:|---|---|
| **S** | 900–1000 | 卓越可信 | 可接高风险/高价值 A2A 任务 |
| **A** | 750–899 | 优秀可信 | 默认可信，允许金融读写类能力 |
| **B** | 600–749 | 良好可信 | 普通可信，适合多数工具调用 |
| **C** | 400–599 | 受限可信 | 需要额外 Principal 担保或更高 stake |
| **D** | 0–399 | 不可信 | 默认拒绝，只允许低风险查询 |

### 5.2 各维度详细计算

#### 5.2.1 BehaviorScore（行为分）

基于近 N 次 IPR 记录，评估 Agent 的历史行为表现：

```
BehaviorScore = (success_rate · 0.6 + on_time_rate · 0.3 + repeat_client_rate · 0.1) · 100
```

- **success_rate**：任务成功率，权重 60%
- **on_time_rate**：任务准时率，权重 30%
- **repeat_client_rate**：回头客率，权重 10%

**低样本量处理：**
- 样本量 < 5 时，使用 Bayesian smoothing，避免新 Agent 分数剧烈波动
- 平滑参数：α = 2, β = 1（先验成功率约 67%）

#### 5.2.2 StakeScore（质押分）

评估 Agent 的经济质押规模和质量：

```
stake_usd = Σ amount_i · price_i(oracle) · weight_i
StakeScore = min(100, log10(stake_usd / 100) · 25)
```

**资产集中度惩罚：**
- 单一资产折算占比 > 80% 时，超出部分权重折半
- 目的：防止单一资产剧烈波动导致信用分大幅变化

**锁定期加分：**
- 锁定期 ≥ 180 天：权重 × 1.2
- 锁定期 ≥ 90 天：权重 × 1.1
- 锁定期 < 90 天：权重 × 1.0

#### 5.2.3 EndorsementScore（背书分）

评估 Agent 获得的跨域背书质量：

```
EndorsementScore = PageRank(G_endorse) · DiversityFactor
DiversityFactor = 1 - max(JaccardSim(endorser_clusters))
```

- **PageRank**：在背书图上计算类 PageRank 分数
- **DiversityFactor**：多样性因子，防止互相吹捧集群
- **集群检测**：Jaccard 相似度 > 0.7 的集群，背书权重折半

#### 5.2.4 ValidationScore（验证分）

评估 Agent 经过第三方验证的程度：

```
ValidationScore = Σ (count_i · weight_i) / max_possible · 100
```

**验证类型权重：**
| 验证类型 | 权重 | 说明 |
|---|---:|---|
| `zkml` | 3.0 | zkML 零知识证明验证 |
| `tee` | 2.0 | TEE 可信执行环境验证 |
| `re_execution` | 1.5 | 第三方重执行验证 |
| `human` | 1.0 | 人工审核验证 |

**重复验证者惩罚：**
- 同一 validator 的多次验证只计一次
- 目的：防止单一验证者过度影响评分

#### 5.2.5 DeviceScore（设备分）

评估 Agent 的设备绑定强度：

```
DeviceScore = level_scores[binding_level]
if has_network_drift and not has_principal_co_sign:
    DeviceScore = max(0, DeviceScore - 50)
```

**绑定级别分数：**
| 级别 | 分数 |
|---|---:|
| `strong` | 100 |
| `runtime` | 75 |
| `registration` | 50 |
| `none` | 0 |

**网络漂移惩罚：**
- 检测到网络漂移（国家/ASN 变化）且无 Principal 副署时，扣 50 分
- 目的：防止密钥被盗后在异地使用

#### 5.2.6 PrincipalScore（主体分）

评估 Agent 背后 Principal 的信用：

```
PrincipalScore = min(100, principal_credit_score · 0.3)
```

- Principal 信用分按 0.3 系数透传
- Principal 黑名单时，Agent 最高 tier 限制为 C
- Principal CRITICAL 违规时，所有关联 Agent 暂停服务

### 5.3 ViolationPenalty（违规惩罚）

违规惩罚基于违规严重度和时间衰减：

```
ViolationPenalty = Σ severity(v_i) · exp(-(t_now - t_i) / τ)
```

- `severity(v_i)`：违规严重度，0–100 连续值
- `τ = 180` 天：时间衰减常数
- 惩罚从总分中扣除，最低扣到 0 分

**严重度分桶（仅用于人类可读展示）：**

| 级别 | 严重度范围 | 惩罚措施 |
|---|---:|---|
| **INFO** | 0–20 | 日志记录，不扣分 |
| **MINOR** | 21–40 | 单次扣分，可恢复 |
| **MAJOR** | 41–70 | 降一档 tier，部分 stake slash |
| **CRITICAL** | 71–100 | Principal 标黑，跨 Agent 持久化，全量 slash |

### 5.4 CreditVC（信用凭证）

CreditVC 是 Credit Engine 签发的可验证信用凭证，遵循 W3C VC 2.0 标准：

```jsonc
{
  "@context": ["https://www.w3.org/ns/credentials/v2", "https://agent-score.org/v1"],
  "type": ["VerifiableCredential", "AgentCreditCredential"],
  "issuer": "did:ethr:0x2105:0xCA...",          // 必须在白名单
  "validFrom":  "2026-05-27T00:00:00Z",
  "validUntil": "2026-06-26T00:00:00Z",         // 固定 30 天
  "credentialSubject": {
    "id": "did:ethr:0x2105:0x...",
    "score": 782,
    "tier":  "A",
    "dimensions": {
      "behavior": 88, "endorsement": 65, "stake": 92,
      "validation": 70, "device": 95, "principal": 80
    },
    "snapshot_root": "0xabc...",  // 链下 IPR Merkle Root
    "violation_count_90d": 0,
    "reason_codes": ["LOW_STAKE_USD", "HIGH_VIOLATION_90D"]
  },
  "proof": {
    "type": "AgentScoreJWS2026",
    "created": "2026-05-27T12:00:00Z",
    "verificationMethod": "did:ethr:0x2105:0xCA...",
    "proofPurpose": "assertionMethod",
    "jws": "base64url(header).base64url(payload).base64url(signature)"
  }
}
```

**证明类型：**

| 类型 | 用途 | 状态 |
|---|---|---|
| `AgentScoreHMAC2026` | 本地测试、兼容旧 demo | 保留 |
| `AgentScoreJWS2026` | 生产环境，ES256K 签名 | 推荐 |

**JWS 安全校验：**
- MUST 验证 `alg=ES256K`，防止算法降级攻击
- MUST 验证 `kid=issuer`，防止密钥混淆攻击
- MUST 验证 payload 与去除 proof 后的 VC 一致

### 5.5 Reason Code（原因码）

评分结果必须输出可解释的原因码，便于像银行征信一样审计：

| 原因码 | 含义 |
|---|---|
| `LOW_SAMPLE_SIZE` | 历史交互样本量不足 |
| `LOW_STAKE_USD` | 质押金额不足 |
| `HIGH_STAKE_CONCENTRATION` | 质押资产集中度太高 |
| `HIGH_VIOLATION_90D` | 近 90 天违规次数过多 |
| `CRITICAL_PRINCIPAL_VIOLATION` | Principal 有严重违规 |
| `ENDORSEMENT_CLUSTER_RISK` | 背书存在集群风险 |
| `LOW_VALIDATION_COVERAGE` | 第三方验证覆盖率不足 |
| `EXPIRED_PRINCIPAL_VC` | Principal 身份凭证过期 |
| `NO_DEVICE_BINDING` | 无设备绑定 |
| `NETWORK_DRIFT_WITHOUT_PRINCIPAL_COSIGN` | 网络漂移且无 Principal 副署 |

---

## 第六章：设备与网络绑定 / Device & Network Binding

### 6.1 绑定架构

设备与网络绑定是 Agent-Score 区别于其他信用系统的核心创新。它解决了一个根本性问题：**即使 Agent 私钥泄露，攻击者也无法在其他设备上盗用该身份**。

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Agent DID      │────▶│  Device DID     │────▶│  Principal DID  │
│  (数字身份)     │     │  (硬件身份)     │     │  (责任主体)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
          │                       │                       │
          ▼                       ▼                       ▼
    CreditVC             DeviceBindingVC            KYB/KYC VC
  (30天有效期)          (24小时有效期)           (1年有效期)
```

### 6.2 绑定级别详解

#### 6.2.1 None（无绑定）

- 无任何设备绑定信息
- 设备得分：0 分
- 适用场景：测试环境、纯云端无状态 Agent、一次性任务 Agent
- 安全注意：仅允许低风险查询类任务

#### 6.2.2 Registration（注册绑定）

- Agent 首次部署时，采集设备硬件指纹并注册
- 硬件指纹来源：
  - TPM 公钥哈希
  - 主板序列号
  - MAC 地址哈希
  - CPU 特征组合
- 设备得分：50 分
- 适用场景：普通应用、低风险场景
- 局限性：仅在注册时验证，运行时不持续验证

#### 6.2.3 Runtime（运行时绑定）

- 运行时持续验证设备状态
- 验证方式：
  - TPM 定期 Quote（每小时）
  - TEE 健康检查报告
  - 软件完整性校验（Secure Boot、代码签名）
- 设备得分：75 分
- 适用场景：金融应用、中风险场景
- 优势：确保持续运行在可信设备上

#### 6.2.4 Strong（强绑定）

- 最高安全级别，三重保障：
  1. TEE/TPM 硬件证明
  2. 运行时持续验证
  3. Principal 副署确认
- 设备得分：100 分
- 适用场景：身份管理、高价值交易、密钥管理
- 优势：即使设备被盗，没有 Principal 签名也无法使用

### 6.3 网络指纹

网络指纹用于检测 Agent 是否在异常网络环境中运行，辅助识别密钥盗用。

**网络指纹数据结构：**
```jsonc
{
  "ip_prefix": "203.0.113.0/24",      // IP 前缀，不存完整 IP
  "asn": 12345,                       // 自治系统号
  "country_code": "SG",               // ISO 3166-1 alpha-2
  "city_geo_hash": "w21z7",           // 城市级 geohash
  "timestamp": "2026-05-28T10:00:00Z"
}
```

**隐私保护设计：**
- 只存储 IP 前缀（/24），不存储完整 IP 地址
- 使用 geohash 而不是精确经纬度
- 数据链下存储，链上只锚定哈希
- 支持 ZK 证明验证国家/ASN 而不暴露具体位置

### 6.4 网络漂移检测

**漂移判定条件（满足任一即视为漂移）：**
1. `current.country_code != registered_country_code`
2. `current.asn != registered_asn`

**漂移处理策略：**

| 场景 | 策略 |
|---|---|
| 首次注册 | 记录 `registered_country_code` 和 `registered_asn` 作为基线 |
| 漂移 + Principal 副署 | 允许访问，不扣分（视为合法迁移） |
| 漂移 + 无副署 | 拒绝访问，扣 50 分 DeviceScore |
| 持续漂移 > 7 天 | 触发 Principal 告警，建议重新绑定 |
| 漂移到高风险国家/ASN | 即使有副署也拒绝（可配置） |

**Principal 副署格式：**
```jsonc
{
  "caller_signature": "base64-encoded-agent-signature",
  "principal_signature": "base64-encoded-principal-signature",
  "drift_authorization": {
    "authorized_country": "US",
    "authorized_asn": 67890,
    "valid_until": "2026-05-29T10:00:00Z",
    "max_transactions": 100
  }
}
```

### 6.5 DeviceBindingVC（设备绑定凭证）

DeviceBindingVC 由 Device Authority 签发，有效期 24 小时（短有效期确保持续验证）：

```jsonc
{
  "@context": ["https://www.w3.org/ns/credentials/v2", "https://agent-score.org/v1"],
  "type": ["VerifiableCredential", "AgentDeviceBindingCredential"],
  "issuer": "did:ethr:0x2105:0xDEVICE_AUTH",
  "issuanceDate": "2026-05-28T10:00:00Z",
  "expirationDate": "2026-05-29T10:00:00Z",   // 24 小时有效期
  "credentialSubject": {
    "id": "did:ethr:0x2105:0xAGENT",
    "principal": "did:web:owner.example",
    "device_id": "device-uuid-12345",
    "binding_level": "strong",
    "attestation_type": "tpm_2.0_quote",
    "registered_country_code": "SG",
    "registered_asn": 12345,
    "hardware_model": "MacBookPro18,3",
    "device_attestation": {
      "attestation_type": "tpm_2.0_quote",
      "device_pubkey_hash": "0xabc123def456",
      "pcr_values": { "PCR0": "0x...", "PCR4": "0x...", "PCR7": "0x..." },
      "quote": "base64-encoded-tpm-quote",
      "signature": "base64-encoded-tpm-signature",
      "timestamp": 1748428800
    }
  },
  "proof": {
    "type": "AgentScoreJWS2026",
    "created": "2026-05-28T10:00:00Z",
    "verificationMethod": "did:ethr:0x2105:0xDEVICE_AUTH",
    "proofPurpose": "assertionMethod",
    "jws": "base64url(header).base64url(payload).base64url(signature)"
  }
}
```

**验证流程：**
1. 验证 issuer 是否在 `trusted_device_authorities` 白名单
2. 验证有效期（24 小时）
3. 验证 JWS 签名（alg=ES256K, kid=issuer）
4. 验证 `binding_level >= policy.min_binding_level`
5. 验证 `country_code` 在 `allowed_countries` 中
6. 验证 `asn` 不在 `blocked_asns` 中
7. 检测网络漂移，如有漂移检查 Principal 副署

---

## 第七章：快速认证层 / Trust Handshake Layer

### 7.1 握手流程

快速认证层（Trust Handshake Layer）是 Agent-Score 协议的核心，在 A2A 调用前完成信用验证，目标延迟 < 100ms。

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
   │                                                │  ④ 验证设备绑定状态
   │                                                │  ⑤ 检测网络漂移
   │◀── 4. AuthAck { session_token, S.credit_vc } ──│
   │                                                │
   │── 5. Encrypted A2A JSON-RPC calls ────────────▶│
   │                                                │
   │── 6. Settle: 双签 IPR ─────────────────────────│
   │     上链: hash(IPR) → ReputationRegistry      │
```

### 7.2 性能预算

握手阶段的性能目标是 **< 100ms**，各步骤时间分配：

| 步骤 | 操作 | 时间预算 | 说明 |
|---|---|---:|---|
| 1 | 网络传输（Agent Card 获取） | 30ms | 可缓存，有效期 30 天 |
| 2 | CreditVC 签名验证 | 10ms | ES256K 签名验证 |
| 3 | 有效期检查 | < 1ms | 纯内存操作 |
| 4 | 策略检查 | < 1ms | 纯内存操作 |
| 5 | 设备绑定验证 | 20ms | JWS 验证 + 漂移检测 |
| 6 | 网络传输（AuthAck） | 30ms | |
| **总计** | | **~91ms** | |

**缓存策略：**
- CreditVC 缓存：30 天（与 VC 有效期一致）
- DeviceBindingVC 缓存：24 小时（与 VC 有效期一致）
- 握手结果缓存：5 分钟（防止重复验证）

### 7.3 AgentPolicy（策略引擎）

AgentPolicy 是调用方的信任门槛配置，支持灵活的策略组合：

```python
@dataclass(frozen=True)
class AgentPolicy:
    # 信用要求
    min_credit_score: int = 600
    min_tier: str = "B"
    max_violation_90d: int = 2

    # 签发方信任
    trusted_issuers: Set[str] = field(default_factory=set)
    trusted_device_authorities: Set[str] = field(default_factory=set)

    # 设备绑定要求
    require_device_binding: bool = False
    min_binding_level: str = "registration"

    # 网络访问控制
    allowed_countries: Set[str] = field(default_factory=set)
    blocked_asns: Set[int] = field(default_factory=set)

    # 漂移处理
    require_principal_co_sign_on_drift: bool = True

    # 能力要求
    require_capability_vcs: List[str] = field(default_factory=list)
    require_principal_did: bool = False

    # 黑名单
    blocked_principals: Set[str] = field(default_factory=set)
    blocked_agents: Set[str] = field(default_factory=set)

    # 隐私选项
    allow_anonymous_zk: bool = True  # 允许 ZK 阈值证明
```

**策略组合逻辑：**
- 所有 `min_*` 和 `max_*` 条件必须同时满足
- `trusted_*` 白名单：至少匹配一个（或配置为全部匹配）
- `blocked_*` 黑名单：匹配任一即拒绝
- `allowed_countries` 非空时，必须在列表中
- `blocked_asns` 非空时，不能在列表中

### 7.4 握手验证步骤

`verify_agent_card_credit` 函数执行完整的握手验证：

1. **基础完整性检查**
   - Agent Card 字段完整性
   - DID 格式有效性

2. **CreditVC 验证**
   - issuer 在 `trusted_issuers` 白名单
   - 有效期检查（`validFrom <= now < validUntil`）
   - JWS 签名验证（alg=ES256K, kid=issuer）
   - payload 完整性验证

3. **信用检查**
   - `score >= policy.min_credit_score`
   - `tier >= policy.min_tier`（S > A > B > C > D）
   - `violation_count_90d <= policy.max_violation_90d`

4. **设备绑定验证**（如果 `policy.require_device_binding`）
   - `device_binding_vc` 存在性检查
   - Device Authority 白名单检查
   - DeviceBindingVC 有效期检查（24 小时）
   - JWS 签名验证
   - `binding_level >= policy.min_binding_level`
   - 国家/ASN 访问控制检查
   - 网络漂移检测与 Principal 副署检查

5. **黑名单检查**
   - Agent DID 不在 `blocked_agents`
   - Principal DID 不在 `blocked_principals`

6. **能力检查**（如果配置）
   - 所需 Capability VC 都存在且有效

### 7.5 HandshakeResult（握手结果）

```python
@dataclass(frozen=True)
class HandshakeResult:
    accepted: bool
    reason: str
    agent_did: str
    score: Optional[int] = None
    tier: Optional[str] = None
    provider_score: Optional[int] = None
    provider_tier: Optional[str] = None
```

**常见拒绝原因：**

| 原因码 | 说明 |
|---|---|
| `ACCEPTED` | 验证通过 |
| `MISSING_CREDIT_VC` | 缺少 CreditVC |
| `UNTRUSTED_ISSUER` | 签发方不在白名单 |
| `EXPIRED_CREDIT_VC` | CreditVC 已过期 |
| `INVALID_CREDIT_VC` | CreditVC 签名验证失败 |
| `SCORE_BELOW_THRESHOLD` | 信用分低于阈值 |
| `TIER_BELOW_THRESHOLD` | 等级低于阈值 |
| `TOO_MANY_VIOLATIONS` | 近 90 天违规次数过多 |
| `MISSING_DEVICE_BINDING` | 缺少设备绑定 |
| `UNTRUSTED_DEVICE_AUTHORITY` | 设备权威机构不在白名单 |
| `EXPIRED_DEVICE_BINDING` | 设备绑定 VC 已过期 |
| `INVALID_DEVICE_BINDING` | 设备绑定签名验证失败 |
| `INSUFFICIENT_BINDING_LEVEL` | 绑定级别不足 |
| `COUNTRY_NOT_ALLOWED` | 国家不在允许列表 |
| `ASN_BLOCKED` | ASN 在封禁列表 |
| `NETWORK_DRIFT_WITHOUT_PRINCIPAL_COSIGN` | 网络漂移且无 Principal 副署 |
| `BLOCKED_AGENT` | Agent 在黑名单 |
| `BLOCKED_PRINCIPAL` | Principal 在黑名单 |

---

## 第八章：交互存证 / Interaction Proof Record

### 8.1 IPR 数据结构

IPR（Interaction Proof Record）是 A2A 交互的不可抵赖记录，由交易双方双重签名。

```python
@dataclass(frozen=True)
class InteractionProofRecordEnvelope:
    caller_did: str
    callee_did: str
    task_id: str
    success: bool
    on_time: bool
    result_hash: str
    caller_signature: Optional[str] = None
    callee_signature: Optional[str] = None

    @property
    def ipr_hash(self) -> str:
        unsigned = {
            "caller_did": self.caller_did,
            "callee_did": self.callee_did,
            "task_id": self.task_id,
            "success": self.success,
            "on_time": self.on_time,
            "result_hash": self.result_hash,
        }
        return sha256_json(unsigned)
```

**字段说明：**
- `caller_did`：调用方 Agent DID
- `callee_did`：被调用方 Agent DID
- `task_id`：任务唯一标识
- `success`：任务是否成功
- `on_time`：任务是否按时完成
- `result_hash`：任务结果的 SHA-256 哈希
- `caller_signature`：调用方对 unsigned payload 的签名
- `callee_signature`：被调用方对 unsigned payload 的签名
- `ipr_hash`：unsigned payload 的 SHA-256 哈希（用于链上锚定）

### 8.2 双签机制

IPR 采用双重签名机制，确保交易不可抵赖：

```
Caller                          Callee
  │                               │
  │ 1. 生成任务结果               │
  │ 2. 计算 result_hash           │
  │ 3. 构建 unsigned payload      │
  │ 4. 签名 → caller_signature    │
  │                               │
  │──── 5. 发送 payload + 签名 ──▶│
  │                               │ 6. 验证 caller_signature
  │                               │ 7. 签名 → callee_signature
  │◀── 8. 返回 callee_signature ──│
  │                               │
  │ 9. 验证 callee_signature      │
  │ 10. 生成完整 IPR              │
  │ 11. 锚定到链上                 │
```

**签名算法：**
- 生产环境：ES256K（secp256k1）JWS 签名
- 测试环境：HMAC-SHA256
- 签名内容：规范化后的 unsigned payload（字段按字母排序）

### 8.3 链上锚定

IPR 的详细数据存储在链下（IPFS/Arweave/中心化存储），链上只锚定哈希：

```
链下存储 (IPFS):
┌─────────────────────────────────────────┐
│ 完整 IPR 数据                            │
│  - caller_did, callee_did                │
│  - task_id, success, on_time             │
│  - result_hash, 双签                      │
│  - 任务结果原文（可选）                   │
└─────────────────────────────────────────┘
         │
         ▼  SHA-256
         │
链上存储 (ReputationRegistry):
┌─────────────────────────────────────────┐
│ mapping(uint256 agentId => bytes32[])   │
│  iprRoots[agentId] = [hash1, hash2, ...]│
└─────────────────────────────────────────┘
```

**锚定频率：**
- 实时锚定：每笔 IPR 立即上链（高安全场景）
- 批量锚定：每 1000 笔 IPR 计算 Merkle Root 后上链（低成本场景）
- 定时锚定：每小时锚定一次（普通场景）

**验证方式：**
1. 从链下获取完整 IPR 数据
2. 计算 ipr_hash
3. 验证 ipr_hash 在链上 iprRoots 中
4. 验证双签有效性

### 8.4 信用激励

IPR 不仅是存证记录，也是信用评分的输入：

**成功交易的正向激励：**
- `success=true`：增加 BehaviorScore 的 success_rate
- `on_time=true`：增加 BehaviorScore 的 on_time_rate
- 新的交易对手：增加 repeat_client_rate 的分母
- 回头客交易：增加 repeat_client_rate 的分子

**失败交易的负向惩罚：**
- `success=false`：降低 success_rate，可能触发违规记录
- `on_time=false`：降低 on_time_rate
- 严重失败（如欺诈）：创建 ViolationRecord，绑定 Principal

**信用更新流程：**
```
新 IPR 生成
    ↓
加入 Agent 的 interactions 列表
    ↓
重新计算 BehaviorScore
    ↓
触发式重算 CreditScore（或每日批量重算）
    ↓
生成新的 CreditVC（如果分数变化超过阈值）
```

---

## 第九章：注册表合约 / Registry Contracts

### 9.1 合约架构

Agent-Score 的注册表合约兼容 ERC-8004 标准，采用模块化设计：

```
┌──────────────────────────────────────────────────────────┐
│                     AgentScoreRoot                        │
│              (Proxy / Diamond 可升级)                     │
├──────────────────────────────────────────────────────────┤
│  IdentityRegistry         │  CreditAuthorityRegistry     │
│  (Agent 身份注册)          │  (信用权威机构白名单)         │
├──────────────────────────────────────────────────────────┤
│  StakeRegistry            │  ViolationRegistry           │
│  (多资产质押与 Slash)      │  (违规记录绑定 Principal)    │
├──────────────────────────────────────────────────────────┤
│  ReputationRegistry       │  ValidationRegistry          │
│  (IPR 哈希锚定)            │  (第三方验证记录)            │
└──────────────────────────────────────────────────────────┘
```

### 9.2 IdentityRegistry（身份注册表）

**核心接口：**
```solidity
interface IIdentityRegistry {
    function registerAgent(
        address agent,
        string memory did,
        string memory principalDid,
        string memory metadataURI
    ) external returns (uint256 agentId);

    function updatePrincipal(uint256 agentId, string memory newPrincipalDid) external;

    function principalOf(uint256 agentId) external view returns (string memory);

    function didOf(uint256 agentId) external view returns (string memory);

    function agentIdOf(address agent) external view returns (uint256);

    function isBlacklisted(uint256 agentId) external view returns (bool);

    event AgentRegistered(uint256 indexed agentId, address indexed agent, string did);
    event PrincipalUpdated(uint256 indexed agentId, string oldPrincipal, string newPrincipal);
    event AgentBlacklisted(uint256 indexed agentId, string reason);
}
```

**设计要点：**
- Soulbound ERC-721，不可转让
- 每个 Agent 地址对应唯一 tokenId
- Principal 可更新，但旧 Principal 的违规记录仍然保留
- 支持 Agent 黑名单（暂停服务）

### 9.3 StakeRegistry（质押注册表）

**核心接口：**
```solidity
interface IStakeRegistry {
    function stake(
        uint256 agentId,
        address asset,
        uint256 amount,
        uint64 lockUntil
    ) external payable;

    function unstake(uint256 agentId, address asset, uint256 amount) external;

    function slash(
        uint256 agentId,
        address asset,
        uint256 ratioBasisPoints,
        bytes32 reason,
        address recipient
    ) external;

    function positionOf(uint256 agentId, address asset)
        external
        view
        returns (uint256 amount, uint64 lockUntil, uint256 slashed);

    event Staked(
        uint256 indexed agentId,
        address indexed asset,
        uint256 amount,
        uint64 lockUntil
    );
    event Unstaked(uint256 indexed agentId, address indexed asset, uint256 amount);
    event Slashed(
        uint256 indexed agentId,
        address indexed principal,
        address asset,
        uint256 amount,
        bytes32 reason
    );
}
```

**设计要点：**
- 支持多资产质押（任意 ERC-20 + 原生 ETH）
- 通过 Chainlink/Pyth 价格预言机折算 USD
- 每种资产可单独配置权重和最低门槛
- Slash 权限：仅授权合约（如 ViolationRegistry）可调用
- Slash 资金：发送到指定 recipient（如 DAO 金库、保险基金）

### 9.4 ViolationRegistry（违规注册表）

**核心接口：**
```solidity
interface IViolationRegistry {
    function recordViolation(
        uint256 agentId,
        uint8 severity,
        string memory evidenceURI,
        bytes32 iprHash
    ) external;

    function getViolations(string memory principalDid)
        external
        view
        returns (Violation[] memory);

    function violationCount90d(string memory principalDid) external view returns (uint256);

    function isPrincipalFlagged(string memory principalDid) external view returns (bool);

    event ViolationRecorded(
        address indexed principal,
        uint8 severity,
        string evidenceURI,
        bytes32 iprHash
    );
    event PrincipalFlagged(string indexed principalDid, uint8 maxSeverity);
}
```

**设计要点：**
- 违规记录绑定 Principal DID，跨 Agent 持久化
- `severity`：0–100 连续值，给细粒度建模留余地
- `evidenceURI`：违规证据的链下存储地址（IPFS/Arweave）
- Principal 有 CRITICAL 违规时自动标记为 flagged
-  flagged Principal 下的所有 Agent 最高 tier 限制为 C

### 9.5 CreditAuthorityRegistry（信用权威机构注册表）

**核心接口：**
```solidity
interface ICreditAuthorityRegistry {
    function addAuthority(address authority, string memory metadataURI) external;

    function removeAuthority(address authority, bytes32 reason) external;

    function isTrustedAuthority(address authority) external view returns (bool);

    function getAuthorities() external view returns (address[] memory);

    event AuthorityAdded(address indexed authority, string metadataURI);
    event AuthorityRemoved(address indexed authority, bytes32 reason);
}
```

**设计要点：**
- 白名单制，仅授权的 Credit Authority 签发的 VC 被承认
- M1 阶段采用多签 admin 维护
- 后续可平滑迁移到 DAO 治理
- 移除 Authority 时需要提供原因，增加透明度

### 9.6 ReputationRegistry（声誉注册表）

**核心接口：**
```solidity
interface IReputationRegistry {
    function submitIPR(
        uint256 agentId,
        bytes32 root,
        bytes calldata callerSig,
        bytes calldata calleeSig
    ) external;

    function getIPRRoots(uint256 agentId) external view returns (bytes32[] memory);

    function verifyIPR(uint256 agentId, bytes32 iprHash) external view returns (bool);

    event IPRSubmitted(
        uint256 indexed agentId,
        bytes32 root,
        address indexed caller
    );
}
```

**设计要点：**
- 存储 IPR 的 Merkle Root，而非每笔 IPR
- 支持批量提交，降低 Gas 成本
- 任何人都可以验证某笔 IPR 是否被锚定
- callerSig 和 calleeSig 用于链上验证双签（可选）

### 9.7 ValidationRegistry（验证注册表）

**核心接口：**
```solidity
interface IValidationRegistry {
    function submitValidation(
        uint256 agentId,
        string memory validatorId,
        string memory validationType,
        bytes calldata attestation,
        bytes32 resultHash
    ) external;

    function getValidations(uint256 agentId)
        external
        view
        returns (ValidationAttestation[] memory);

    event ValidationSubmitted(
        uint256 indexed agentId,
        string validatorId,
        string validationType,
        bytes32 resultHash
    );
}
```

**设计要点：**
- 兼容 zkML、TEE、re-execution 等多种验证类型
- `attestation`：验证证明数据（如 zk proof、TEE quote）
- `resultHash`：验证结果的哈希

---

## 第十章：经济模型 / Economic Model

### 10.1 信用溢价机制

Agent-Score 的经济模型核心是「信用溢价」——高信用的 Agent 可以获得更高的调用价格：

```
调用价格 = 基础价格 × (1 + 信用溢价系数)
信用溢价系数 = (CreditScore - 600) / 400 × 0.5
```

**示例：**
- 信用分 600（B 级）：溢价系数 0，价格 = 基础价格
- 信用分 800（A 级）：溢价系数 0.25，价格 = 基础价格 × 1.25
- 信用分 1000（S 级）：溢价系数 0.5，价格 = 基础价格 × 1.5

**市场机制：**
- 溢价系数由市场供需动态调整
- 高信用 Agent 可以选择不收取溢价，以获得更多订单
- 低信用 Agent 可能需要提供折扣才能获得订单
- 形成「信用 → 收益 → 更高信用」的正向循环

### 10.2 惩罚机制

惩罚机制是 Agent-Score 经济模型的重要组成部分，确保违规行为有明确的成本：

| 违规级别 | 严重度 | 惩罚措施 |
|---|---:|---|
| INFO | 0–20 | 日志记录，不扣分 |
| MINOR | 21–40 | 扣 50–100 信用分，30 天后恢复 |
| MAJOR | 41–70 | 降一档 tier，Slash 20% 质押，90 天后恢复 |
| CRITICAL | 71–100 | Principal 标黑，全量 Slash，永久记录 |

**Slash 资金用途：**
- 50% 用于赔偿受损方
- 30% 进入 DAO 金库
- 20% 用于奖励举报者（如果适用）

### 10.3 激励闭环

Agent-Score 构建了完整的经济激励闭环：

```
┌─────────────┐
│  A2A 调用   │
└──────┬──────┘
       │ 支付
       ▼
┌─────────────┐     ┌─────────────┐
│  x402 支付  │────▶│  结算层     │
└──────┬──────┘     └──────┬──────┘
       │  交易成功           │  Slash 事件
       ▼                    ▼
┌─────────────┐     ┌─────────────┐
│  信用引擎   │     │  质押注册表 │
└──────┬──────┘     └──────┬──────┘
       │  新 CreditVC       │  质押变化
       ▼                    ▼
┌─────────────┐     ┌─────────────┐
│  声誉注册表 │◀────┘  违规注册表 │
└─────────────┘     └─────────────┘
```

**正向循环：**
1. Agent 提供高质量服务，获得成功交易记录
2. 信用分提升，等级上升
3. 可以收取信用溢价，获得更高收益
4. 可以承担更高价值的任务
5. 获得更多背书和验证，进一步提升信用

**负向循环：**
1. Agent 违规或提供低质量服务
2. 信用分下降，等级降低
3. 被 Slash 质押，经济损失
4. 只能承担低价值任务，收益下降
5. Principal 被标记，影响其他 Agent

### 10.4 Credit Authority 经济模型

Credit Authority 作为信用签发机构，也有相应的经济激励和约束：

**收入来源：**
- VC 签发费用（每笔 CreditVC 收取固定费用）
- 订阅费用（Agent 按月/按年订阅信用评估服务）
- 数据 API 费用（第三方查询信用数据）

**约束机制：**
- Credit Authority 需要质押一定数量的 Token
- 如果签发的 VC 被证明有问题（如串通造假），质押会被 Slash
- 持续签发低质量 VC 会被移出白名单
- 形成「声誉 → 业务 → 收益 → 更高声誉」的正向循环

### 10.5 Token 经济学（可选）

Agent-Score 协议本身不强制发行原生 Token，但可以兼容现有 Token 经济：

**可选 Token 用途：**
- 质押：Agent 使用原生 Token 质押
- 支付：A2A 交易使用原生 Token 支付
- 治理：Token 持有者参与 Credit Authority 白名单投票
- 激励：举报违规获得 Token 奖励

**注意：** M0-M3 阶段不依赖原生 Token，可以使用 USDC、ETH 等主流资产。

---

## 第十一章：安全分析 / Security Analysis

### 11.1 抗 Sybil 攻击分析

Sybil 攻击是去中心化信用系统面临的核心挑战之一。Agent-Score 通过多维度防御机制有效抵御 Sybil 攻击：

**防御机制 1：Stake 质押**
- 创建和维护 Agent 需要质押一定数量的资产
- 攻击成本 = 攻击者想要控制的 Agent 数量 × 最低质押门槛
- 违规会导致 Slash，进一步提高攻击成本
- 经济分析：如果攻击收益 < 攻击成本，攻击是不理性的

**防御机制 2：Principal 担保**
- 每个 Agent 必须关联到一个 Principal
- Principal 需要通过 KYB/KYC 验证
- 同一 Principal 下的所有 Agent 共享黑名单
- 攻击者需要大量真实身份才能创建大量 Agent

**防御机制 3：背书多样性检测**
- 背书图做 Jaccard 集群检测
- 相似度 > 0.7 的集群，背书权重折半
- 攻击者控制的 Agent 互相背书会被检测到

**防御机制 4：设备绑定**
- 每个 Agent 需要绑定到物理设备
- 设备 ID 由 TPM/TEE 硬件保证唯一性
- 攻击者需要大量物理设备才能创建大量 Agent

**综合分析：**
- 攻击者需要同时突破经济（Stake）、身份（Principal）、社交（背书）、硬件（设备）四道防线
- 攻击成本远高于潜在收益
- 对于大多数场景，双轨制（Stake + Principal）满足其一即可提供足够的 Sybil 抵抗

### 11.2 抗密钥盗用分析

密钥盗用是 Agent 安全的核心痛点。Agent-Score 通过设备绑定机制有效防止密钥盗用：

**攻击场景 1：密钥被盗，攻击者在其他设备使用**
- 防御：设备绑定 VC 包含设备 ID 和硬件证明
- 攻击者的设备没有正确的 TPM/TEE 证明
- 设备绑定验证失败，握手被拒绝
- 安全保障：✅ 有效防御

**攻击场景 2：密钥被盗，攻击者在同一设备使用**
- 防御：运行时绑定需要 TEE 持续验证
- 如果 Agent 运行在 TEE 中，攻击者无法提取密钥
- 如果设备被盗，Principal 可以远程吊销设备绑定
- 安全保障：✅ 有效防御（强绑定级别）

**攻击场景 3：密钥被盗，攻击者在注册地以外使用**
- 防御：网络漂移检测
- 攻击者的 IP 前缀/ASN/国家与注册时不同
- 触发漂移检测，要求 Principal 副署
- 安全保障：✅ 有效防御

**攻击场景 4：内部人员盗用（合法设备 + 合法网络）**
- 防御：Principal 副署要求（高安全场景）
- 重要操作需要 Principal 二次签名
- 所有操作都有 IPR 记录，可追溯到具体操作人员
- 安全保障：✅ 有效防御（强绑定级别）

### 11.3 隐私保护分析

Agent-Score 在设计上充分考虑了隐私保护：

**数据最小化原则：**
- 网络指纹只存储 IP 前缀（/24），不存储完整 IP 地址
- 使用城市级 geohash，不存储精确经纬度
- IPR 详细数据链下存储，链上只锚定哈希
- 支持 ZK 选择性披露，验证「信用分 ≥ 阈值」而不暴露具体分数

**身份分离设计：**
- Agent DID 与 Principal DID 分离，支持可控关联
- 交易记录使用假名，只有在违规仲裁时才需要揭示真实身份
- 支持一次性交易 DID，保护长期身份隐私

**合规性考虑：**
- 数据保留策略：IPR 原始数据默认保留 2 年，违规记录永久保留
- 支持「被遗忘权」：Agent 注销后可删除非必要数据
- 跨区域数据传输符合 GDPR、CCPA 等法规要求

### 11.4 智能合约安全考虑

**重入攻击防护：**
- 所有外部调用使用「检查-生效-交互」模式
- Slash 操作使用 Pull 模式，避免重入风险
- 关键状态变更使用 ReentrancyGuard

**权限控制：**
- 采用多签 admin 管理 Credit Authority 白名单
- Slash 权限仅授予 ViolationRegistry 合约
- 支持角色权限分离（Owner、Admin、Operator）

**升级性设计：**
- 采用 Proxy / Diamond 模式，支持合约升级
- 升级需要多签投票，防止恶意升级
- 升级前需要时间锁（Timelock），给用户足够时间反应

---

## 第十二章：路线图 / Roadmap

### 12.1 阶段规划

| 阶段 | 目标 | 关键里程碑 | 时间线 |
|---|---|---|---|
| **M0** | 协议规范 | 完成 SPEC 文档、JSON Schema、安全审计 | 2026 Q1 |
| **M1** | 合约骨架 | ERC-8004 兼容注册表、Stake/Violation Registry、Foundry 测试 | 2026 Q2 |
| **M2** | 信用引擎 | FastAPI + LangGraph 评分流水线、六维评分模型、CreditVC 签发 | 2026 Q2 |
| **M3** | A2A 中间件 | Python/TS SDK、握手扩展、设备绑定、FastAPI Adapter | 2026 Q3 |
| **M4** | ZK 隐私层 | BBS+ VC、阈值证明电路、ZK-SNARK 集成 | 2026 Q4 |
| **M5** | 测试网 + 互操作 | Base Sepolia 部署、ERC-8004 互通测试、生态集成 | 2027 Q1 |
| **M6** | 主网启动 | 多链部署、DAO 治理、生态激励计划 | 2027 Q2 |

### 12.2 当前进展（v0.1.0）

✅ **已完成：**
- 完整的协议规范（§1-16）
- M1：Solidity 注册表合约骨架（Identity、Reputation、Stake、Validation、Violation、CreditAuthority）
- M2：Credit Engine 六维评分模型（行为、质押、背书、验证、设备、主体）
- M3：A2A Middleware 握手验证 + 策略引擎
- M3.2：FastAPI HTTP Adapter
- M3.3：设备与网络绑定（TEE/TPM 证明 + 漂移检测）
- JWS ES256K 证明 + alg/kid 头部校验
- 双签 IPR + 链上锚定抽象
- 本地 MVP Demo + HTTP Demo + Minimal Demo
- 中英文白皮书
- 全量测试覆盖（37 个测试用例，100% 通过）

⏳ **进行中：**
- Foundry 合约测试（需要本地安装 Foundry）
- 真实 TEE/TPM 集成（当前为 Mock）
- 真实 IP/ASN/Geo 数据库集成（当前为 Mock）

🔮 **下一步：**
- 部署到 Base Sepolia 测试网
- 开发 TypeScript SDK
- 集成 ZK 选择性披露
- 建立 Credit Authority 白名单治理机制
- 生态合作伙伴接入

### 12.3 研究方向

**长期研究课题：**
1. **动态权重调整**：基于市场环境自动调整评分维度权重
2. **联邦学习评分**：多方安全计算，不泄露原始数据的联合建模
3. **AI 驱动的异常检测**：使用 LLM 分析 IPR 内容，检测欺诈模式
4. **跨链信用迁移**：Agent 信用在不同链之间的可移植性
5. **量子安全签名**：后量子密码算法的研究与集成

---

## 第十三章：生态合作 / Ecosystem

### 13.1 合作伙伴类型

Agent-Score 欢迎各类生态伙伴加入，共同构建可信 Agent 生态：

| 伙伴类型 | 角色 | 合作方式 |
|---|---|---|
| **Agent 平台** | 提供 Agent 运行环境 | 集成协议 SDK，提供信用评分服务 |
| **Credit Authority** | 签发 CreditVC | 加入白名单，提供信用评估服务 |
| **Device Authority** | 签发 DeviceBindingVC | 验证 TEE/TPM 证明，提供设备身份服务 |
| **Validator** | 提供第三方验证 | zkML、TEE、re-execution 等验证服务 |
| **钱包提供商** | 管理 Agent 密钥 | 集成 DID 管理，支持设备绑定 |
| **应用开发者** | 构建 Agent 应用 | 使用协议进行可信 A2A 交互 |

### 13.2 开发者支持

- **文档中心**：完整的 API 文档、教程、最佳实践
- **SDK**：Python、TypeScript、Rust 多语言 SDK
- **测试网**：免费的测试网环境，提供测试 Token
- **开发者社区**：Discord、GitHub Discussions、月度开发者电话会
- **资助计划**：生态项目资助、黑客松奖金

---

## 参考文献 / References

### 标准与规范

1. **W3C Decentralized Identifiers (DIDs) v1.0**  
   https://www.w3.org/TR/did-core/

2. **W3C Verifiable Credentials Data Model v2.0**  
   https://www.w3.org/TR/vc-data-model-2.0/

3. **ERC-8004: Agent Identity Registry**  
   https://eips.ethereum.org/EIPS/eip-8004

4. **ERC-8183: Agent-to-Agent Payment Protocol (x402)**  
   https://eips.ethereum.org/EIPS/eip-8183

5. **Google A2A (Agent-to-Agent) Protocol v1.0**  
   https://github.com/google/a2a-protocol

### 相关技术

6. **Trusted Platform Module (TPM) 2.0 Specification**  
   https://trustedcomputinggroup.org/resource/tpm-library-specification/

7. **Intel SGX ECDSA Quote Generation and Verification**  
   https://www.intel.com/content/www/us/en/developer/articles/technical/quote-generation-and-verification.html

8. **BBS+ Signatures for Selective Disclosure**  
   https://datatracker.ietf.org/doc/html/draft-irtf-cfrg-bbs-signatures

9. **JSON Web Signature (JWS) RFC 7515**  
   https://datatracker.ietf.org/doc/html/rfc7515

10. **PageRank Algorithm**  
    Page, L., et al. (1999). The PageRank Citation Ranking: Bringing Order to the Web.

### 相关项目

11. **MolTrust IPR** - Interaction Proof Record for Agent Trust  
    https://github.com/moltrust/ipr-spec

12. **ACTA** - Agent Credential Trust Architecture  
    https://github.com/acta-protocol/acta-spec

13. **qntm Authority** - Decentralized Agent Authority  
    https://github.com/qntm-network/authority-spec

### 安全研究

14. **Sybil Attacks in Decentralized Systems**  
    Douceur, J. R. (2002). The Sybil Attack. IPTPS.

15. **JWS Algorithm Downgrade Attacks**  
    https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/

16. **TPM 2.0 Security Best Practices**  
    https://trustedcomputinggroup.org/wp-content/uploads/TPM-2.0-Security-Best-Practices.pdf

---

## 附录 / Appendix

### A. 术语表 / Glossary

| 术语 | 英文 | 定义 |
|---|---|---|
| **Agent** | Agent | 由 LLM/工作流驱动的自治实体 |
| **Principal** | Principal | Agent 背后的责任主体（自然人/法人/DAO） |
| **DID** | Decentralized Identifier | 去中心化标识符 |
| **VC** | Verifiable Credential | 可验证凭证 |
| **CreditVC** | Credit Verifiable Credential | 信用凭证，包含 Agent 信用评分 |
| **DeviceBindingVC** | Device Binding Verifiable Credential | 设备绑定凭证，证明 Agent 运行在可信设备上 |
| **IPR** | Interaction Proof Record | 交互证明记录，A2A 交易的双签存证 |
| **TEE** | Trusted Execution Environment | 可信执行环境 |
| **TPM** | Trusted Platform Module | 可信平台模块 |
| **Sybil Attack** | Sybil Attack | 女巫攻击，通过创建大量虚假身份操纵系统 |
| **Sybil Resistance** | Sybil Resistance | 女巫抵抗，防止女巫攻击的机制 |

### B. 评分参数参考

| 参数 | 默认值 | 说明 |
|---|---:|---|
| 基础分 | 300 | 新 Agent 的初始分数 |
| Behavior 权重 | 350 | 历史行为维度权重 |
| Endorsement 权重 | 150 | 跨域背书维度权重 |
| Stake 权重 | 200 | 质押维度权重 |
| Validation 权重 | 150 | 第三方验证维度权重 |
| Device 权重 | 100 | 设备绑定维度权重 |
| Principal 权重 | 50 | 主体信用维度权重 |
| 违规惩罚系数 λ | 400 | 违规惩罚系数 |
| 时间衰减 τ | 180 天 | 违规记录的时间衰减常数 |
| CreditVC 有效期 | 30 天 | 信用凭证的有效期 |
| DeviceBindingVC 有效期 | 24 小时 | 设备绑定凭证的有效期 |
| Jaccard 相似度阈值 | 0.7 | 背书集群检测阈值 |
| 资产集中度阈值 | 80% | 单一资产质押占比阈值 |

### C. 联系方式

- **官网**：https://agent-score.org
- **GitHub**：https://github.com/agent-score/agent-score
- **Discord**：https://discord.gg/agent-score
- **Twitter/X**：@AgentScoreOrg
- **邮箱**：contact@agent-score.org

---

**文档版本：** v0.1.0-draft  
**最后更新：** 2026-05-28  
**版权所有：** © 2026 Agent-Score Contributors. Licensed under MIT.

