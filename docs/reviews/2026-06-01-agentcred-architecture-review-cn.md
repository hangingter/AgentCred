# AgentCred 架构审查表

> Date: 2026-06-01  
> Scope: 技术评审、架构 review、尽调初筛  
> Status: Review Snapshot

## 审查结论

**总体判断**：AgentCred 是一个把 **DID / VC / Agent 信用评分 / A2A 门控 / 链上 registry** 组合起来的 **原型级协议实现**。方向清晰，模块划分不错，代码不是空壳；但当前仍明显处于 **MVP / PoC** 阶段。其主要问题不在“有没有想法”，而在于 **身份根、证据根、链上闭环、撤销治理、标准互操作** 这几个关键点还没真正做实。

**是否适合生产**：**不适合直接生产落地**  
**是否适合研究/PoC**：**适合**  
**最关键短板**：**Trust 根不够硬，证据可验证性不够，链上与链下未闭环**

## 优先级分布

- **P0（必须先解决）**：4 项
- **P1（严重缺口）**：4 项
- **P2（工程成熟度问题）**：2 项

## 问题审查表

| 优先级 | 问题 | 现象 / 证据 | 影响 | 建议 | 修复难度 |
|---|---|---|---|---|---|
| **P0** | **IPR 签名模型过弱** | `ipr.py` 里证据签名本质是共享 secret/HMAC 风格，不是 DID 私钥签名、JWS 或 EIP-712 | 无法形成真正公开可验证的交互证据；“可审计/可追责”基础不足 | 将 IPR 升级为 **JWS 或 EIP-712 typed data**；签名主体应绑定 agent DID / wallet；链上 anchor 记录可验证签名摘要而不只是 hash | 中 |
| **P0** | **DID 只停留在字符串层** | 大量使用 `did:ethr:`，但没有 DID resolver、DID Document 拉取、verification method 验证 | 去中心化身份根不成立；issuer/agent 对 DID 的控制关系无法真实验证 | 接入 **did:ethr resolver**；所有 issuer / agent / device authority 的 key 从 DID Document 动态解析；支持 key rotation | 高 |
| **P0** | **链上与链下未真正闭环** | middleware 和 credit engine 不读取链上 authority / identity / validation 状态，trust 主要靠内存配置与本地 key | 链上 registry 无法成为统一事实源；协议可信性被削弱 | 在 middleware 中直接查询 **CreditAuthorityRegistry / IdentityRegistry / ValidationRegistry**；引入链上缓存层或 indexer | 高 |
| **P0** | **VC 缺少撤销机制** | 没有 credential status / revocation list / 吊销查询 | 已失效或泄露的 credential 仍可能被接受；不适合生产治理 | 增加 **credentialStatus**；支持链上/链下 revocation registry；握手时强制校验 credential status | 中 |
| **P1** | **IdentityRegistry 非严格标准兼容** | `IdentityRegistry.sol` 更像自定义 soulbound registry，不是完整 ERC-721 / ERC-165 / EIP-8004 实现 | 难与标准工具、索引器、钱包互操作；标准化迁移成本高 | 重构为 **标准兼容 identity registry**；保留 `didOf/principalOf` 作为扩展 | 高 |
| **P1** | **A2A 集成不完整** | 主要通过 `AgentCard + x-agent-score + /a2a` 集成，缺少完整 A2A 消息模型、会话、能力协商 | 只能跑受控 demo；难以接入真实多方 A2A 网络 | 明确对齐目标版本；补齐 **标准 A2A 消息层、错误模型、会话语义** | 高 |
| **P1** | **Device binding 过度 demo 化** | fake attestation 数据、有效期与文档不一致、验证逻辑复用 Credit VC verifier | 设备信任语义被高估；无法支撑真实 TEE/attestation 场景 | 将设备凭证独立成 **Device Attestation VC**；接入真实 attestation 验证链；规范有效期和 trust level | 中-高 |
| **P1** | **信用评分缺少真实数据闭环** | score 规则清楚，但输入多为 demo / 内存对象，缺少链上事件和外部 validator 自动接入 | 抗操纵能力有限；信用分更像样例，不足以支撑高价值 trust 决策 | 将链上 stake / validation / violation / IPR 事件接入评分；引入 reviewer/validator 权重模型 | 中 |
| **P2** | **API 模型与底层模型不一致** | 底层 `CreditInput` 支持更多字段，如 `device`，但 API request 未完整暴露 | 服务行为与底层能力不一致，增加使用和维护成本 | 对齐 API 与底层模型；补齐 schema 和字段校验；做版本管理 | 低 |
| **P2** | **命名与工程组织仍在过渡期** | 仓库叫 AgentCred，但包名/文档/配置仍大量保留 `agent-score` | 降低工程成熟度观感，增加维护和外部采用成本 | 完成一次统一重构：仓库名、包名、文档名、发布名、导入路径一致化 | 低 |

## 重点审查意见

### 一、是否真的“可信”

**当前答案：还不够。**

原因不是因为没有评分、没有 VC、没有链上合约，而是：

1. **身份根不够硬**：DID 没有真正 resolve
2. **证据根不够硬**：IPR 不是公开可验证签名
3. **治理根不够硬**：VC 不能有效撤销
4. **信任根不够硬**：链上 registry 没有真正进入 runtime decision path

### 二、是否真的“去中心化”

**当前答案：接口形态偏去中心化，但运行时实质仍偏中心化。**

因为很多关键点仍然依赖：

- 本地 secret
- 内存 trusted issuer 配置
- 本地 key map
- demo stub anchor

所以现在更准确的说法是：

> **它是“面向去中心化 trust 协议的原型”，而不是已经实现的去中心化 trust network。**

### 三、最值得保留的部分

这项目不是没有价值，反而有几个很值得保留：

1. **评分引擎结构清楚、可解释**
2. **JWS VC 这部分实现相对扎实**
3. **A2A middleware 切点选得对**
4. **Principal + Violation 的设计有现实意义**
5. **链上 registry 的模块拆分方向合理**

也就是说：**骨架是对的，根基还没打牢。**

## 建议的修复顺序

### 第 1 阶段：先补齐信任根（必须）

1. IPR 改为公开可验证签名
2. DID resolution 落地
3. VC revocation/status 落地
4. middleware 读链上 authority / identity

### 第 2 阶段：补齐互操作

5. IdentityRegistry 标准化
6. A2A 完整协议化
7. 设备 attestation 独立建模

### 第 3 阶段：补齐生产化

8. 评分数据闭环
9. API / schema 对齐
10. 命名、文档、发布体系统一

## Roadmap View

| 阶段 | 目标 | 对应风险 | 交付物 |
|---|---|---|---|
| Trust Root Hardening | 让身份、证据、撤销、链上 authority 进入 runtime 决策路径 | P0 | DID resolver、JWS/EIP-712 IPR、credentialStatus、registry reader |
| Interop Roadmap | 让协议能接入标准工具链和真实 A2A 网络 | P1 | 标准 IdentityRegistry、A2A message/session/error model、Device Attestation VC |
| Production Cleanup | 让工程形态、数据闭环和外部接入达到可维护状态 | P2 | event/indexer 数据源、API schema 对齐、AgentCred 命名统一 |

## 最终一句话结论

> **AgentCred 是一个值得关注的 Agent trust 协议原型，但当前更像“有清晰方向的研究型 MVP”，而不是可直接支撑开放 Agent 经济的生产级基础设施。**
