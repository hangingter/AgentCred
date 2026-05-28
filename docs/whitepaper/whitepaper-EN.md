# Agent-Score: Banking-Grade Credit Protocol for AI Agents

**Version:** 0.1.0  
**Date:** 2026-05-28  
**Status:** Draft for Review  
**Authors:** Agent-Score Contributors

---

## Executive Summary

With the explosive growth of AI Agent technology, autonomous agents are becoming core participants in the digital economy. However, the Agent ecosystem faces a significant trust gap: how to ensure Agent identities are trustworthy, behaviors are accountable, and transactions are traceable? Existing reputation systems mostly rely on centralized platforms, lacking hardware-level security binding, making it difficult to prevent key theft and Sybil attacks.

**Agent-Score** is a decentralized credit protocol for AI Agents, designed to build a banking-grade Agent credit system. The protocol integrates W3C DID/VC standards, ERC-8004 registries, and Google A2A communication protocols, and innovatively introduces a **device and network binding** mechanism, achieving a complete trust chain: **Agent → Device → Owner**.

**Core Innovations:**

1. **Six-Dimensional Credit Scoring Model**: Behavior, Stake, Endorsement, Validation, Device, Principal — comprehensive assessment of Agent trustworthiness
2. **Hardware-Level Identity Binding**: TEE/TPM device attestation + network fingerprint drift detection, preventing key theft
3. **Fast Authentication Layer**: < 100ms handshake verification, supporting real-time trust decisions in A2A scenarios
4. **Accountable System**: Dual-signed IPR for every transaction, violation records bound to Principal, persistent across Agent lifecycles
5. **Dual-Track Sybil Resistance**: Stake + Principal guarantee, dual-track parallelism effectively resists Sybil attacks

Agent-Score provides complete trust infrastructure for the Agent ecosystem, enabling Agents to conduct trusted transactions in open networks as if they have "ID cards" and "credit reports".

---

## Chapter 1: Introduction

### 1.1 The Explosion of AI Agents and the Trust Gap

In recent years, Large Language Models (LLMs) and Multi-Agent Systems have made breakthrough progress. From AutoGPT to CrewAI, from LangGraph to Google A2A, AI Agents are moving from proof-of-concept to production applications. Agents are no longer simple chatbots, but digital entities capable of autonomously executing complex tasks:

- **Trading Agents**: Automatically execute trading strategies in DeFi protocols
- **Service Agents**: Provide professional services such as legal consultation, medical diagnosis, and data analysis
- **Collaboration Agents**: Cross-departmental collaboration within enterprises, completing end-to-end business processes
- **Creative Agents**: Generate code, designs, copywriting, and other creative content

However, with the explosive growth in the number of Agents, a fundamental problem becomes increasingly prominent: **How to trust a stranger Agent?**

In traditional Internet services, trust is endorsed by centralized platforms. But in decentralized Agent ecosystems:
- Agents may be created and controlled by anonymous entities
- Agent behaviors lack transparent audit trails
- Key leakage may lead to Agent identity theft
- Malicious Agents may engage in fraud, market manipulation, and other behaviors
- Difficult to trace the real responsible party after violations

### 1.2 Limitations of Existing Solutions

Existing Agent reputation and trust solutions have many limitations:

| Solution | Advantages | Limitations |
|---|---|---|
| **Centralized Reputation Systems** | Simple implementation, large user base | Data silos, platform monopoly, privacy leakage risk |
| **On-Chain Pure Reputation** | Decentralized, transparent | Vulnerable to Sybil attacks, no hardware binding, high computational cost |
| **Token Staking Mechanism** | Clear economic incentives | High capital threshold, staking asset volatility risk |
| **ZK Anonymous Proofs** | Good privacy protection | High computational complexity, poor user experience |

In particular, existing solutions generally lack **hardware-level identity binding** — even if an Agent has a DID identity, once the private key is leaked, attackers can use the identity on any device. This is unacceptable for high-security scenarios such as finance and healthcare.

### 1.3 The Mission of Agent-Score

The mission of Agent-Score is to build a **banking-grade credit system** for AI Agents, such that:

- ✅ **Trusted Identity**: Each Agent has a verifiable DID identity, linked to a real responsible party
- ✅ **Quantifiable Credit**: Accurate assessment of Agent trustworthiness through multi-dimensional scoring models
- ✅ **Device Binding**: Agent identity strongly bound to hardware devices, preventing key theft
- ✅ **Traceable Transactions**: Dual-signed evidence for every interaction, anchored on-chain, non-repudiable
- ✅ **Accountable Violations**: Violation records bound to responsible parties, persistent across Agents, forming effective deterrence
- ✅ **Privacy Protection**: Support ZK selective disclosure, protecting privacy while verifying credit

Agent-Score does not reinvent the wheel, but stands on the shoulders of giants:
- Identity layer reuses **W3C DID** and **ERC-8004** standards
- Credential layer adopts **W3C Verifiable Credentials**
- Communication layer is compatible with **Google A2A v1.0** protocol
- Settlement layer interfaces with **ERC-8183 (x402)** payment standard

By building open, compatible, and secure trust infrastructure, Agent-Score is committed to promoting the AI Agent ecosystem from "barbaric growth" to "trusted prosperity".

---

## Chapter 2: Design Principles

### 2.1 No Reinventing the Wheel

Agent-Score maximizes reuse of mature industry standards and open-source components, reducing ecosystem integration friction:

- **Identity Layer**: Directly reuse `did:ethr:` method, no custom DID Method
- **Credential Layer**: Follow W3C VC 2.0 standard, compatible with existing VC ecosystem
- **Communication Layer**: Compatible with Google A2A v1.0 through `x-agent-score` extension field
- **Contract Layer**: Compatible with ERC-8004 registry interface, smooth migration possible
- **Payment Layer**: Interface with x402 / ERC-8183 payment standards

### 2.2 Light on Chain, Heavy off Chain

To balance security, performance, and cost, Agent-Score adopts a "light on chain, heavy off chain" architecture:

- **On-Chain**: Only anchor key states such as identity, credit snapshots, violation records, and stakes
- **Off-Chain**: Computationally intensive operations such as credit scoring, IPR batch processing, and VC issuance
- **Anchoring Mechanism**: Merkle Root of off-chain computation results is periodically anchored on-chain, ensuring verifiability

This design ensures:
- Controllable on-chain Gas costs
- Credit scoring can be complex and sophisticated (six dimensions, real-time updates)
- Off-chain computation is reproducible and auditable
- No sacrifice of final security and immutability

### 2.3 Privacy First

Agent-Score takes privacy protection as a core design goal:

- **ZK Selective Disclosure**: Use BBS+ signatures, support zero-knowledge proofs of "credit score ≥ threshold" without exposing specific scores
- **Data Minimization**: Network fingerprints only store IP prefixes (/24) and city-level geohashes, no full IP storage
- **Off-Chain Evidence**: IPR detailed data stored off-chain, only hashes anchored on-chain
- **Identity Separation**: Agent DID separated from Principal DID, supporting controllable association

### 2.4 Dual-Track Sybil Resistance

Agent-Score adopts a "Stake + Principal guarantee" dual-track system to effectively resist Sybil attacks:

| Track | Mechanism | Applicable Scenarios |
|---|---|---|
| **Track A — Stake** | Agent locks ≥ threshold, Slash on violation | Open/anonymous scenarios, DeFi trading |
| **Track B — Principal Guarantee** | Principal endorses with real identity VC (KYB/KYC) | B2B scenarios, financial services |

Callers can configure "at least one" or "both" through policy.

Additional hard constraints:
- All Agents under the same Principal share a blacklist
- Jaccard cluster detection on endorsement graphs, endorsement weights halved for similarity > 0.7
- When single asset stake ratio > 80%, excess portion weight is halved

### 2.5 Accountable

The core design philosophy of Agent-Score is "every A2A interaction is traceable to the Principal":

- **IPR Dual Signing**: Every interaction requires dual signatures from caller and callee
- **Principal Association**: Each Agent DID is associated with a Principal DID (natural person/legal entity/DAO)
- **Violation Persistence**: Violation records bound to Principal, persistent across Agent lifecycles
- **Graded Penalties**: Different levels of penalties based on violation severity (0–100), from point deduction to full Slash

This design ensures that even if an Agent is deregistered or abandoned, the responsible party behind it can still be traced and held accountable.

---

## Chapter 3: System Architecture

### 3.1 Five-Layer Architecture Model

Agent-Score adopts a clear five-layer architecture, with each layer having clear responsibilities and loose coupling:

```
┌──────────────────────────────────────────────────────────┐
│  L5  Application       Business Agents (LangGraph / CrewAI…) │
│                                                          │
│  Business Logic Layer: Specific Agent applications, calling lower-layer protocols for trusted interactions │
├──────────────────────────────────────────────────────────┤
│  L4  Communication     Google A2A v1.0 (Agent Card, JSON-RPC)│
│                                                          │
│  Communication Layer: Message transmission protocol between Agents, compatible with Google A2A standard │
├──────────────────────────────────────────────────────────┤
│  L3  Trust Handshake   Agent-Score Handshake Extension (core of this specification)│
│                                                          │
│  Fast Authentication Layer: < 100ms to complete credit verification and policy check │
├──────────────────────────────────────────────────────────┤
│  L2  Credit Engine     Scoring Model + VC Issuance (off-chain)        │
│                                                          │
│  Credit Engine Layer: Six-dimensional scoring, CreditVC issuance, Reason Code generation │
├──────────────────────────────────────────────────────────┤
│  L1  Registries        Identity / Reputation / Validation│
│                        / Stake / Violation (ERC-8004 compatible)│
│                                                          │
│  Registry Layer: On-chain contracts, anchoring key states such as identity, credit, violations, stakes │
├──────────────────────────────────────────────────────────┤
│  L0  Settlement        EVM L2 (Base / OP / Arbitrum)    │
│                                                          │
│  Settlement Layer: Underlying blockchain, providing finality and immutability guarantees │
└──────────────────────────────────────────────────────────┘
```

### 3.2 Core Components

#### 3.2.1 Identity Registry

- Soulbound Token based on ERC-721, each Agent corresponds to a tokenId
- Stores key information such as Agent DID, Principal DID, Operator DID
- Supports bidirectional queries `principalOf(agentId)` and `didOf(agentId)`
- Compatible with ERC-8004 standard interface

#### 3.2.2 Credit Engine

- Off-chain deterministic scoring, input and output are reproducible and auditable
- Six-dimensional scoring model: Behavior, Stake, Endorsement, Validation, Device, Principal
- Issues CreditVC with 30-day validity, supports both HMAC and JWS proof methods
- Outputs Reason Codes, providing bank-level interpretability

#### 3.2.3 A2A Middleware

- Agent Card parsing and verification
- CreditVC integrity, validity, issuer whitelist verification
- Configurable policy engine (credit score threshold, tier requirements, device binding requirements, etc.)
- IPR dual signature generation and hash calculation
- FastAPI HTTP Adapter for quick integration with existing services

#### 3.2.4 Device Authority

- Verifies TEE/TPM device attestations
- Issues DeviceBindingVC with 24-hour validity
- Maintains device blacklists (stolen devices, compromised TEEs, etc.)
- Supports distributed trust model with multiple device authorities

### 3.3 Protocol Flow

The complete Agent-Score protocol flow includes six phases:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Identity   │ →  │  Credit     │ →  │  Handshake  │
│ Declaration │    │  Assessment │    │  Verification│
└─────────────┘    └─────────────┘    └─────────────┘
       ↓                  ↓                  ↓
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Settlement │ ←  │  Execution  │ ←  │  Credit     │
│  & Evidence │    │             │    │  Incentive  │
└─────────────┘    └─────────────┘    └─────────────┘
```

1. **Identity Declaration**: Agent generates DID, registers with Identity Registry, associates Principal
2. **Credit Assessment**: Credit Engine calculates credit score based on historical data, issues CreditVC
3. **Handshake Verification**: Before transaction, caller verifies counterparty's CreditVC and device binding status
4. **Transaction Execution**: After successful handshake, execute specific A2A tasks
5. **Credit Incentive**: Successful transactions improve both parties' credit scores, violations result in point deductions and Slash
6. **Settlement & Evidence**: Generate dual-signed IPR, hash anchored to on-chain Reputation Registry

### 3.4 Trust Chain

Agent-Score builds a complete trust chain, ensuring security at every layer:

```
Principal (Natural Person/Legal Entity)
    ↓ Real Identity VC (KYB/KYC)
Agent DID
    ↓ Device Binding VC (TEE/TPM Attestation)
CreditVC (Six-Dimensional Credit Score)
    ↓ JWS Signature (alg=ES256K, kid=issuer)
Agent Card
    ↓ Handshake Verification (policy check)
A2A Transaction
    ↓ Dual-Signed IPR
Chain Anchor (Merkle Root)
```

---

## Chapter 4: Identity Layer

### 4.1 DID Method Design Decision

Agent-Score chooses to directly reuse the `did:ethr:` method rather than defining a custom DID Method, based on the following considerations:

**Advantages:**
- ✅ **Mature Ecosystem**: Wallets, resolvers, toolchains are readily available, no need to rebuild
- ✅ **Good Compatibility**: Seamless integration with existing Ethereum ecosystem
- ✅ **High Security**: Battle-tested, clear security boundaries
- ✅ **Low Migration Cost**: Familiar to developers, low barrier to entry

**DID Format:**
```
did:ethr:<chain-id>:<agent-eoa-or-erc4337-address>
example: did:ethr:0x2105:0x8004A169FB4a3325136EB29fA0ceB6D2e539a432
                  └── Base Mainnet (8453 = 0x2105)
```

`agentId` (tokenId of ERC-8004 Identity Registry) and DID are bidirectionally resolved through `IdentityRegistry.didOf(agentId)`.

### 4.2 Agent Passport

Agent Passport is a Soulbound ERC-721 Token, serving as the Agent's "digital passport". Its metadata is anchored to Arweave/IPFS and contains the following information:

```jsonc
{
  // —— Basic Information ——
  "name": "trade-router-agent",
  "version": "1.2.0",
  "description": "Professional DeFi trading routing Agent",
  "avatar": "ipfs://Qm.../avatar.png",

  // —— Identity Information ——
  "did": "did:ethr:0x2105:0x8004A169FB4a3325136EB29fA0ceB6D2e539a432",
  "principal": "did:web:acme.com",         // Parent responsible party
  "operator":  "did:web:ops.acme.com",      // Operator

  // —— Capability Information ——
  "skills": ["routing", "risk-check", "trade.execute"],
  "endpoints": { "a2a": "https://agent.acme.com/a2a" },
  "capability_vcs": ["ipfs://Qm.../cap1.jwt"],

  // —— Credit Information ——
  "credit_vc": "ipfs://Qm.../credit.jwt",   // 30-day validity CreditVC
  "credit_authority": "did:ethr:0x2105:0xCA...",  // Issuing authority

  // —— Device Binding ——
  "device_binding_vc": "ipfs://Qm.../device.jwt",  // 24-hour validity
  "device_fingerprint": "tpm-pubkey-hash-0xabc...",

  // —— Governance Information ——
  "policy_uri": "ipfs://Qm.../policy.json",  // Agent's rejection policy
  "terms_of_service": "ipfs://Qm.../tos.md"
}
```

### 4.3 Principal Association Model

Principal is the responsible party behind an Agent, which can be:
- Natural person (verified through KYC VC)
- Legal entity (verified through KYB VC)
- DAO (verified through multi-sig governance)

**Association Rules:**
1. Each Agent MUST be associated with exactly one Principal
2. A Principal CAN be associated with multiple Agents
3. Principal changes MUST trigger on-chain events, violation records from old associations remain
4. All Agents under a Principal blacklist have a maximum tier limit of C

**Principal Credit Pass-Through:**
- Principal's credit score is passed through to all Agents under them with a coefficient of 0.3
- When a Principal violates rules, all associated Agents' credit scores are affected
- When a Principal is marked CRITICAL, all associated Agents are suspended

### 4.4 Device Binding Mechanism

Device binding is one of Agent-Score's core innovations, ensuring that Agent identity is not only associated with a Principal but also bound to a specific physical device.

**Binding Levels:**

| Level | Description | Device Score | Security Scenario |
|---|---|---:|---|
| `none` | No device binding | 0 | Test environments, stateless cloud Agents |
| `registration` | Bind device hardware fingerprint at registration | 50 | General applications, low-risk scenarios |
| `runtime` | Continuously verify device status at runtime | 75 | Financial applications, medium-risk scenarios |
| `strong` | TEE + runtime verification + Principal signature | 100 | Identity management, high-risk scenarios |

**Device Attestation Format (TPM Quote Example):**
```jsonc
{
  "attestation_type": "tpm_2.0_quote",
  "device_id": "uuid-550e8400-e29b-41d4-a716-446655440000",
  "hardware_model": "MacBookPro18,3",
  "tpm_version": "2.0",
  "pcr_values": {
    "PCR0": "0xabc123...",  // BIOS hash
    "PCR4": "0xdef456...",  // Boot Manager hash
    "PCR7": "0xghi789..."   // Secure Boot configuration
  },
  "quote": "base64-encoded-tpm-quote",
  "signature": "base64-encoded-tpm-signature",
  "timestamp": 1748428800
}
```

**TEE Attestation Format (Intel SGX Example):**
```jsonc
{
  "attestation_type": "sgx_ecdsa_qe3",
  "device_id": "sgx-enclave-hash-0x123...",
  "hardware_model": "Intel Xeon Ice Lake",
  "tee_type": "SGX",
  "mrenclave": "0xabc123def456...",  // Enclave code hash
  "mrsigner": "0x789abcdef012...",   // Signer hash
  "isv_prod_id": 1,
  "isv_svn": 3,
  "quote": "base64-encoded-sgx-quote",
  "signature": "base64-encoded-intel-signature",
  "timestamp": 1748428800
}
```

---

## Chapter 5: Credit Engine

### 5.1 Six-Dimensional Scoring Model

Agent-Score adopts a six-dimensional scoring model to comprehensively assess Agent trustworthiness. Each dimension is scored 0–100, weighted and summed to obtain the final credit score (0–1000).

**Scoring Formula:**
```
CreditScore = clamp(0, 1000,
    300                              // Base score
  + w_b · BehaviorScore               // Historical behavior (35%, 350 points)
  + w_e · EndorsementScore            // Cross-domain endorsement (15%, 150 points)
  + w_s · StakeScore                  // Stake weight (20%, 200 points)
  + w_v · ValidationScore             // Third-party validation (15%, 150 points)
  + w_d · DeviceScore                 // Device binding (10%, 100 points)
  + w_p · PrincipalScore              // Guarantor credit (5%, 50 points)
  - λ  · ViolationPenalty             // Violation deduction (with time decay)
)
```

**Default Weights:**
- `w_b = 350` (Behavior 35%)
- `w_e = 150` (Endorsement 15%)
- `w_s = 200` (Stake 20%)
- `w_v = 150` (Validation 15%)
- `w_d = 100` (Device 10%)
- `w_p = 50` (Principal 5%)
- `λ = 400` (Violation penalty coefficient)

**Score Tiers:**

| Tier | Score Range | Description | Default Policy |
|---|---:|---|---|
| **S** | 900–1000 | Exceptionally Trustworthy | Can take high-risk/high-value A2A tasks |
| **A** | 750–899 | Excellent Trust | Default trusted, allows financial read-write capabilities |
| **B** | 600–749 | Good Trust | Generally trusted, suitable for most tool calls |
| **C** | 400–599 | Limited Trust | Requires additional Principal guarantee or higher stake |
| **D** | 0–399 | Not Trustworthy | Default reject, only low-risk queries allowed |

### 5.2 Detailed Calculation of Each Dimension

#### 5.2.1 BehaviorScore

Based on recent N IPR records, assess the Agent's historical behavior:

```
BehaviorScore = (success_rate · 0.6 + on_time_rate · 0.3 + repeat_client_rate · 0.1) · 100
```

- **success_rate**: Task success rate, weight 60%
- **on_time_rate**: Task punctuality rate, weight 30%
- **repeat_client_rate**: Repeat customer rate, weight 10%

**Low Sample Size Handling:**
- When sample size < 5, use Bayesian smoothing to avoid drastic score fluctuations for new Agents
- Smoothing parameters: α = 2, β = 1 (prior success rate ~67%)

#### 5.2.2 StakeScore

Assess the scale and quality of the Agent's economic stake:

```
stake_usd = Σ amount_i · price_i(oracle) · weight_i
StakeScore = min(100, log10(stake_usd / 100) · 25)
```

**Asset Concentration Penalty:**
- When single asset ratio > 80%, excess portion weight is halved
- Purpose: Prevent drastic credit score changes due to single asset volatility

**Lock-up Period Bonus:**
- Lock-up period ≥ 180 days: weight × 1.2
- Lock-up period ≥ 90 days: weight × 1.1
- Lock-up period < 90 days: weight × 1.0

#### 5.2.3 EndorsementScore

Assess the quality of cross-domain endorsements received by the Agent:

```
EndorsementScore = PageRank(G_endorse) · DiversityFactor
DiversityFactor = 1 - max(JaccardSim(endorser_clusters))
```

- **PageRank**: Calculate PageRank-like score on endorsement graph
- **DiversityFactor**: Diversity factor, preventing mutual admiration clusters
- **Cluster Detection**: For clusters with Jaccard similarity > 0.7, endorsement weights are halved

#### 5.2.4 ValidationScore

Assess the degree of third-party validation the Agent has undergone:

```
ValidationScore = Σ (count_i · weight_i) / max_possible · 100
```

**Validation Type Weights:**
| Validation Type | Weight | Description |
|---|---:|---|
| `zkml` | 3.0 | zkML zero-knowledge proof validation |
| `tee` | 2.0 | TEE trusted execution environment validation |
| `re_execution` | 1.5 | Third-party re-execution validation |
| `human` | 1.0 | Human review validation |

**Duplicate Validator Penalty:**
- Multiple validations from the same validator count only once
- Purpose: Prevent single validator from excessively influencing scores

#### 5.2.5 DeviceScore

Assess the Agent's device binding strength:

```
DeviceScore = level_scores[binding_level]
if has_network_drift and not has_principal_co_sign:
    DeviceScore = max(0, DeviceScore - 50)
```

**Binding Level Scores:**
| Level | Score |
|---|---:|
| `strong` | 100 |
| `runtime` | 75 |
| `registration` | 50 |
| `none` | 0 |

**Network Drift Penalty:**
- When network drift (country/ASN change) is detected without Principal co-signature, deduct 50 points
- Purpose: Prevent key theft and use in different locations

#### 5.2.6 PrincipalScore

Assess the credit of the Principal behind the Agent:

```
PrincipalScore = min(100, principal_credit_score · 0.3)
```

- Principal credit score is passed through with a coefficient of 0.3
- When Principal is blacklisted, Agent's maximum tier is limited to C
- When Principal has CRITICAL violations, all associated Agents are suspended

### 5.3 ViolationPenalty

Violation penalties are based on violation severity and time decay:

```
ViolationPenalty = Σ severity(v_i) · exp(-(t_now - t_i) / τ)
```

- `severity(v_i)`: Violation severity, continuous value 0–100
- `τ = 180` days: Time decay constant
- Penalties are deducted from the total score, minimum deduction to 0 points

**Severity Buckets (for human-readable display only):**

| Level | Severity Range | Penalty Measures |
|---|---:|---|
| **INFO** | 0–20 | Logged, no point deduction |
| **MINOR** | 21–40 | Single point deduction, recoverable |
| **MAJOR** | 41–70 | Downgrade one tier, partial stake slash |
| **CRITICAL** | 71–100 | Principal blacklisted, persistent across Agents, full slash |

### 5.4 CreditVC

CreditVC is a verifiable credit credential issued by the Credit Engine, following the W3C VC 2.0 standard:

```jsonc
{
  "@context": ["https://www.w3.org/ns/credentials/v2", "https://agent-score.org/v1"],
  "type": ["VerifiableCredential", "AgentCreditCredential"],
  "issuer": "did:ethr:0x2105:0xCA...",          // MUST be on whitelist
  "validFrom":  "2026-05-27T00:00:00Z",
  "validUntil": "2026-06-26T00:00:00Z",         // Fixed 30 days
  "credentialSubject": {
    "id": "did:ethr:0x2105:0x...",
    "score": 782,
    "tier":  "A",
    "dimensions": {
      "behavior": 88, "endorsement": 65, "stake": 92,
      "validation": 70, "device": 95, "principal": 80
    },
    "snapshot_root": "0xabc...",  // Off-chain IPR Merkle Root
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

**Proof Types:**

| Type | Purpose | Status |
|---|---|---|
| `AgentScoreHMAC2026` | Local testing, backward compatible with old demos | Retained |
| `AgentScoreJWS2026` | Production, ES256K signature | Recommended |

**JWS Security Verification:**
- MUST verify `alg=ES256K` to prevent algorithm downgrade attacks
- MUST verify `kid=issuer` to prevent key confusion attacks
- MUST verify payload matches VC with proof removed

### 5.5 Reason Codes

Scoring results MUST output interpretable reason codes, facilitating audit like bank credit reporting:

| Reason Code | Meaning |
|---|---|
| `LOW_SAMPLE_SIZE` | Insufficient historical interaction samples |
| `LOW_STAKE_USD` | Insufficient stake amount |
| `HIGH_STAKE_CONCENTRATION` | Stake asset concentration too high |
| `HIGH_VIOLATION_90D` | Too many violations in last 90 days |
| `CRITICAL_PRINCIPAL_VIOLATION` | Principal has critical violation |
| `ENDORSEMENT_CLUSTER_RISK` | Endorsement has cluster risk |
| `LOW_VALIDATION_COVERAGE` | Insufficient third-party validation coverage |
| `EXPIRED_PRINCIPAL_VC` | Principal identity credential expired |
| `NO_DEVICE_BINDING` | No device binding |
| `NETWORK_DRIFT_WITHOUT_PRINCIPAL_COSIGN` | Network drift without Principal co-signature |

---

## Chapter 6: Device & Network Binding

### 6.1 Binding Architecture

Device and network binding is the core innovation that distinguishes Agent-Score from other credit systems. It solves a fundamental problem: **even if an Agent's private key is leaked, attackers cannot use that identity on other devices**.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Agent DID      │────▶│  Device DID     │────▶│  Principal DID  │
│  (Digital ID)   │     │  (Hardware ID)  │     │  (Responsible   │
│                 │     │                 │     │   Party)        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
          │                       │                       │
          ▼                       ▼                       ▼
    CreditVC             DeviceBindingVC            KYB/KYC VC
  (30-day validity)     (24-hour validity)          (1-year validity)
```

### 6.2 Binding Level Details

#### 6.2.1 None

- No device binding information
- Device score: 0 points
- Applicable scenarios: Test environments, stateless cloud Agents, one-time task Agents
- Security note: Only low-risk query tasks allowed

#### 6.2.2 Registration

- When Agent is first deployed, collect and register device hardware fingerprint
- Hardware fingerprint sources:
  - TPM public key hash
  - Motherboard serial number
  - MAC address hash
  - CPU feature combination
- Device score: 50 points
- Applicable scenarios: General applications, low-risk scenarios
- Limitation: Only verified at registration, no continuous runtime verification

#### 6.2.3 Runtime

- Continuously verify device status at runtime
- Verification methods:
  - TPM periodic Quote (hourly)
  - TEE health check reports
  - Software integrity verification (Secure Boot, code signing)
- Device score: 75 points
- Applicable scenarios: Financial applications, medium-risk scenarios
- Advantage: Ensures continuous operation on trusted devices

#### 6.2.4 Strong

- Highest security level, triple guarantee:
  1. TEE/TPM hardware attestation
  2. Runtime continuous verification
  3. Principal co-signature confirmation
- Device score: 100 points
- Applicable scenarios: Identity management, high-value transactions, key management
- Advantage: Even if device is stolen, cannot be used without Principal signature

### 6.3 Network Fingerprint

Network fingerprints are used to detect whether an Agent is running in an abnormal network environment, assisting in identifying key theft.

**Network Fingerprint Data Structure:**
```jsonc
{
  "ip_prefix": "203.0.113.0/24",      // IP prefix, no full IP storage
  "asn": 12345,                       // Autonomous System Number
  "country_code": "SG",               // ISO 3166-1 alpha-2
  "city_geo_hash": "w21z7",           // City-level geohash
  "timestamp": "2026-05-28T10:00:00Z"
}
```

**Privacy Protection Design:**
- Only store IP prefixes (/24), no full IP addresses
- Use geohash instead of precise latitude/longitude
- Data stored off-chain, only hashes anchored on-chain
- Support ZK proof verification of country/ASN without exposing specific location

### 6.4 Network Drift Detection

**Drift Determination Conditions (drift if either is met):**
1. `current.country_code != registered_country_code`
2. `current.asn != registered_asn`

**Drift Handling Strategy:**

| Scenario | Strategy |
|---|---|
| First registration | Record `registered_country_code` and `registered_asn` as baseline |
| Drift + Principal co-signature | Allow access, no points deducted (considered legitimate migration) |
| Drift + No co-signature | Deny access, deduct 50 points from DeviceScore |
| Persistent drift > 7 days | Trigger Principal alert, recommend re-binding |
| Drift to high-risk country/ASN | Deny even with co-signature (configurable) |

**Principal Co-signature Format:**
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

### 6.5 DeviceBindingVC

DeviceBindingVC is issued by Device Authority, with 24-hour validity (short validity ensures continuous verification):

```jsonc
{
  "@context": ["https://www.w3.org/ns/credentials/v2", "https://agent-score.org/v1"],
  "type": ["VerifiableCredential", "AgentDeviceBindingCredential"],
  "issuer": "did:ethr:0x2105:0xDEVICE_AUTH",
  "issuanceDate": "2026-05-28T10:00:00Z",
  "expirationDate": "2026-05-29T10:00:00Z",   // 24-hour validity
  "credentialSubject": {
    "id": "did:ethr:0x2105:0xAGENT",
    "principal": "did:web:owner.example.com",
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

**Verification Process:**
1. Verify issuer is on `trusted_device_authorities` whitelist
2. Verify validity period (24 hours)
3. Verify JWS signature (alg=ES256K, kid=issuer)
4. Verify `binding_level >= policy.min_binding_level`
5. Verify `country_code` is in `allowed_countries`
6. Verify `asn` is not in `blocked_asns`
7. Detect network drift, check Principal co-signature if drifted

---

## Chapter 7: Trust Handshake Layer

### 7.1 Handshake Flow

The Trust Handshake Layer is the core of the Agent-Score protocol, completing credit verification before A2A calls, with target latency < 100ms.

```
Caller(C)                                       Callee(S)
   │                                                │
   │── 1. GET /agent-card (A2A standard) ──────────▶│
   │◀── 2. AgentCard + x-agent-score extension ─────│
   │                                                │
   │── 3. AuthInit { nonce, caller_did, caller_vc} ▶│
   │                                                │  ① Verify caller_did signature
   │                                                │  ② Verify caller credit_vc
   │                                                │     · issuer on whitelist
   │                                                │     · not expired & not revoked
   │                                                │     · score >= S.policy.min_score
   │                                                │  ③ Check violation_count_90d
   │                                                │  ④ Verify device binding status
   │                                                │  ⑤ Detect network drift
   │◀── 4. AuthAck { session_token, S.credit_vc } ──│
   │                                                │
   │── 5. Encrypted A2A JSON-RPC calls ────────────▶│
   │                                                │
   │── 6. Settle: Dual-signed IPR ─────────────────│
   │     On-chain: hash(IPR) → ReputationRegistry  │
```

### 7.2 Performance Budget

The performance target for the handshake phase is **< 100ms**, with time allocation for each step:

| Step | Operation | Time Budget | Notes |
|---|---|---:|---|
| 1 | Network transmission (Agent Card fetch) | 30ms | Cacheable, 30-day validity |
| 2 | CreditVC signature verification | 10ms | ES256K signature verification |
| 3 | Validity check | < 1ms | Pure memory operation |
| 4 | Policy check | < 1ms | Pure memory operation |
| 5 | Device binding verification | 20ms | JWS verification + drift detection |
| 6 | Network transmission (AuthAck) | 30ms | |
| **Total** | | **~91ms** | |

**Caching Strategy:**
- CreditVC cache: 30 days (consistent with VC validity)
- DeviceBindingVC cache: 24 hours (consistent with VC validity)
- Handshake result cache: 5 minutes (prevent repeated verification)

### 7.3 AgentPolicy (Policy Engine)

AgentPolicy is the caller's trust threshold configuration, supporting flexible policy combinations:

```python
@dataclass(frozen=True)
class AgentPolicy:
    # Credit requirements
    min_credit_score: int = 600
    min_tier: str = "B"
    max_violation_90d: int = 2

    # Issuer trust
    trusted_issuers: Set[str] = field(default_factory=set)
    trusted_device_authorities: Set[str] = field(default_factory=set)

    # Device binding requirements
    require_device_binding: bool = False
    min_binding_level: str = "registration"

    # Network access control
    allowed_countries: Set[str] = field(default_factory=set)
    blocked_asns: Set[int] = field(default_factory=set)

    # Drift handling
    require_principal_co_sign_on_drift: bool = True

    # Capability requirements
    require_capability_vcs: List[str] = field(default_factory=list)
    require_principal_did: bool = False

    # Blacklists
    blocked_principals: Set[str] = field(default_factory=set)
    blocked_agents: Set[str] = field(default_factory=set)

    # Privacy options
    allow_anonymous_zk: bool = True  # Allow ZK threshold proofs
```

**Policy Combination Logic:**
- All `min_*` and `max_*` conditions must be satisfied simultaneously
- `trusted_*` whitelists: At least one match (or configure for all matches)
- `blocked_*` blacklists: Match any → reject
- When `allowed_countries` is non-empty, must be in list
- When `blocked_asns` is non-empty, must not be in list

### 7.4 Handshake Verification Steps

The `verify_agent_card_credit` function performs complete handshake verification:

1. **Basic Integrity Check**
   - Agent Card field completeness
   - DID format validity

2. **CreditVC Verification**
   - issuer on `trusted_issuers` whitelist
   - Validity check (`validFrom <= now < validUntil`)
   - JWS signature verification (alg=ES256K, kid=issuer)
   - Payload integrity verification

3. **Credit Check**
   - `score >= policy.min_credit_score`
   - `tier >= policy.min_tier` (S > A > B > C > D)
   - `violation_count_90d <= policy.max_violation_90d`

4. **Device Binding Verification** (if `policy.require_device_binding`)
   - `device_binding_vc` existence check
   - Device Authority whitelist check
   - DeviceBindingVC validity check (24 hours)
   - JWS signature verification
   - `binding_level >= policy.min_binding_level`
   - Country/ASN access control check
   - Network drift detection and Principal co-signature check

5. **Blacklist Check**
   - Agent DID not in `blocked_agents`
   - Principal DID not in `blocked_principals`

6. **Capability Check** (if configured)
   - Required Capability VCs all exist and are valid

### 7.5 HandshakeResult

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

**Common Rejection Reasons:**

| Reason Code | Description |
|---|---|
| `ACCEPTED` | Verification passed |
| `MISSING_CREDIT_VC` | Missing CreditVC |
| `UNTRUSTED_ISSUER` | Issuer not on whitelist |
| `EXPIRED_CREDIT_VC` | CreditVC expired |
| `INVALID_CREDIT_VC` | CreditVC signature verification failed |
| `SCORE_BELOW_THRESHOLD` | Credit score below threshold |
| `TIER_BELOW_THRESHOLD` | Tier below threshold |
| `TOO_MANY_VIOLATIONS` | Too many violations in last 90 days |
| `MISSING_DEVICE_BINDING` | Missing device binding |
| `UNTRUSTED_DEVICE_AUTHORITY` | Device authority not on whitelist |
| `EXPIRED_DEVICE_BINDING` | Device binding VC expired |
| `INVALID_DEVICE_BINDING` | Device binding signature verification failed |
| `INSUFFICIENT_BINDING_LEVEL` | Insufficient binding level |
| `COUNTRY_NOT_ALLOWED` | Country not in allowed list |
| `ASN_BLOCKED` | ASN on blocked list |
| `NETWORK_DRIFT_WITHOUT_PRINCIPAL_COSIGN` | Network drift without Principal co-signature |
| `BLOCKED_AGENT` | Agent on blacklist |
| `BLOCKED_PRINCIPAL` | Principal on blacklist |

---

## Chapter 8: Interaction Proof Record

### 8.1 IPR Data Structure

IPR (Interaction Proof Record) is a non-repudiable record of A2A interactions, dual-signed by both transacting parties.

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

**Field Descriptions:**
- `caller_did`: Caller Agent DID
- `callee_did`: Callee Agent DID
- `task_id`: Unique task identifier
- `success`: Whether task succeeded
- `on_time`: Whether task completed on time
- `result_hash`: SHA-256 hash of task result
- `caller_signature`: Caller's signature on unsigned payload
- `callee_signature`: Callee's signature on unsigned payload
- `ipr_hash`: SHA-256 hash of unsigned payload (for on-chain anchoring)

### 8.2 Dual Signature Mechanism

IPR adopts a dual signature mechanism to ensure transaction non-repudiation:

```
Caller                          Callee
  │                               │
  │ 1. Generate task result       │
  │ 2. Calculate result_hash      │
  │ 3. Build unsigned payload     │
  │ 4. Sign → caller_signature    │
  │                               │
  │──── 5. Send payload + sig ───▶│
  │                               │ 6. Verify caller_signature
  │                               │ 7. Sign → callee_signature
  │◀── 8. Return callee_signature │
  │                               │
  │ 9. Verify callee_signature    │
  │ 10. Generate complete IPR     │
  │ 11. Anchor on-chain           │
```

**Signature Algorithm:**
- Production: ES256K (secp256k1) JWS signature
- Testing: HMAC-SHA256
- Signature content: Canonicalized unsigned payload (fields sorted alphabetically)

### 8.3 On-Chain Anchoring

Detailed IPR data is stored off-chain (IPFS/Arweave/centralized storage), only hashes are anchored on-chain:

```
Off-chain Storage (IPFS):
┌─────────────────────────────────────────┐
│ Complete IPR data                       │
│  - caller_did, callee_did                │
│  - task_id, success, on_time             │
│  - result_hash, dual signatures          │
│  - Task result original (optional)       │
└─────────────────────────────────────────┘
         │
         ▼  SHA-256
         │
On-chain Storage (ReputationRegistry):
┌─────────────────────────────────────────┐
│ mapping(uint256 agentId => bytes32[])   │
│  iprRoots[agentId] = [hash1, hash2, ...]│
└─────────────────────────────────────────┘
```

**Anchoring Frequency:**
- Real-time anchoring: Each IPR anchored immediately on-chain (high-security scenarios)
- Batch anchoring: Calculate Merkle Root after every 1000 IPRs then anchor (low-cost scenarios)
- Timed anchoring: Anchor once per hour (normal scenarios)

**Verification Method:**
1. Fetch complete IPR data from off-chain
2. Calculate ipr_hash
3. Verify ipr_hash is in on-chain iprRoots
4. Verify dual signature validity

### 8.4 Credit Incentives

IPR is not only an evidence record but also an input to credit scoring:

**Positive Incentives for Successful Transactions:**
- `success=true`: Increases BehaviorScore's success_rate
- `on_time=true`: Increases BehaviorScore's on_time_rate
- New counterparties: Increases repeat_client_rate denominator
- Repeat customer transactions: Increases repeat_client_rate numerator

**Negative Penalties for Failed Transactions:**
- `success=false`: Decreases success_rate, may trigger violation records
- `on_time=false`: Decreases on_time_rate
- Severe failures (e.g., fraud): Create ViolationRecord, bound to Principal

**Credit Update Flow:**
```
New IPR generated
    ↓
Added to Agent's interactions list
    ↓
Recalculate BehaviorScore
    ↓
Triggered recalculation of CreditScore (or daily batch recalculation)
    ↓
Generate new CreditVC (if score change exceeds threshold)
```

---

## Chapter 9: Registry Contracts

### 9.1 Contract Architecture

Agent-Score's registry contracts are compatible with the ERC-8004 standard, adopting a modular design:

```
┌──────────────────────────────────────────────────────────┐
│                     AgentScoreRoot                        │
│              (Proxy / Diamond Upgradable)                 │
├──────────────────────────────────────────────────────────┤
│  IdentityRegistry         │  CreditAuthorityRegistry     │
│  (Agent Identity Reg)     │  (Credit Authority Whitelist)│
├──────────────────────────────────────────────────────────┤
│  StakeRegistry            │  ViolationRegistry           │
│  (Multi-asset Stake &     │  (Violation Records Bound   │
│   Slash)                  │   to Principal)              │
├──────────────────────────────────────────────────────────┤
│  ReputationRegistry       │  ValidationRegistry          │
│  (IPR Hash Anchoring)     │  (Third-party Validation    │
│                           │   Records)                   │
└──────────────────────────────────────────────────────────┘
```

### 9.2 IdentityRegistry

**Core Interface:**
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

**Design Points:**
- Soulbound ERC-721, non-transferable
- Each Agent address corresponds to a unique tokenId
- Principal can be updated, but violation records from old Principal remain
- Support Agent blacklist (service suspension)

### 9.3 StakeRegistry

**Core Interface:**
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

**Design Points:**
- Support multi-asset staking (any ERC-20 + native ETH)
- Convert to USD through Chainlink/Pyth price oracles
- Each asset can be individually configured with weights and minimum thresholds
- Slash permission: Only authorized contracts (e.g., ViolationRegistry) can call
- Slash funds: Sent to specified recipient (e.g., DAO treasury, insurance fund)

### 9.4 ViolationRegistry

**Core Interface:**
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

**Design Points:**
- Violation records bound to Principal DID, persistent across Agents
- `severity`: Continuous value 0–100, leaving room for fine-grained modeling
- `evidenceURI`: Off-chain storage address for violation evidence (IPFS/Arweave)
- Principal automatically marked as flagged when having CRITICAL violations
- All Agents under flagged Principal have maximum tier limit of C

### 9.5 CreditAuthorityRegistry

**Core Interface:**
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

**Design Points:**
- Whitelist system, only VCs issued by authorized Credit Authorities are recognized
- M1 phase maintained by multi-sig admin
- Subsequent smooth migration to DAO governance
- Reason required when removing Authority, increasing transparency

### 9.6 ReputationRegistry

**Core Interface:**
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

**Design Points:**
- Store Merkle Root of IPRs, not individual IPRs
- Support batch submission, reducing Gas costs
- Anyone can verify whether a specific IPR is anchored
- callerSig and calleeSig for on-chain dual signature verification (optional)

### 9.7 ValidationRegistry

**Core Interface:**
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

**Design Points:**
- Compatible with multiple validation types: zkML, TEE, re-execution, etc.
- `attestation`: Validation proof data (e.g., zk proof, TEE quote)
- `resultHash`: Hash of validation result

---

## Chapter 10: Economic Model

### 10.1 Credit Premium Mechanism

The core of Agent-Score's economic model is "credit premium" — higher credit Agents can obtain higher call prices:

```
Call Price = Base Price × (1 + Credit Premium Coefficient)
Credit Premium Coefficient = (CreditScore - 600) / 400 × 0.5
```

**Examples:**
- Credit score 600 (Tier B): Premium coefficient 0, Price = Base Price
- Credit score 800 (Tier A): Premium coefficient 0.25, Price = Base Price × 1.25
- Credit score 1000 (Tier S): Premium coefficient 0.5, Price = Base Price × 1.5

**Market Mechanism:**
- Premium coefficient dynamically adjusted by market supply and demand
- High credit Agents can choose not to charge premium to get more orders
- Low credit Agents may need to offer discounts to get orders
- Forms a positive cycle of "credit → revenue → higher credit"

### 10.2 Penalty Mechanism

The penalty mechanism is an important part of Agent-Score's economic model, ensuring clear costs for violations:

| Violation Level | Severity | Penalty Measures |
|---|---:|---|
| INFO | 0–20 | Logged, no point deduction |
| MINOR | 21–40 | 50–100 credit points deducted, recoverable after 30 days |
| MAJOR | 41–70 | Downgrade one tier, 20% stake slash, recoverable after 90 days |
| CRITICAL | 71–100 | Principal blacklisted, full slash, permanent record |

**Slash Fund Uses:**
- 50% for compensating affected parties
- 30% to DAO treasury
- 20% for rewarding whistleblowers (if applicable)

### 10.3 Incentive Cycle

Agent-Score builds a complete economic incentive cycle:

```
┌─────────────┐
│  A2A Call   │
└──────┬──────┘
       │ Payment
       ▼
┌─────────────┐     ┌─────────────┐
│  x402 Payment│────▶│  Settlement │
└──────┬──────┘     └──────┬──────┘
       │  Success           │  Slash event
       ▼                    ▼
┌─────────────┐     ┌─────────────┐
│  Credit     │     │  Stake      │
│  Engine     │     │  Registry   │
└──────┬──────┘     └──────┬──────┘
       │  New CreditVC      │  Stake changes
       ▼                    ▼
┌─────────────┐     ┌─────────────┐
│  Reputation │◀────┘  Violation  │
│  Registry   │     │  Registry   │
└─────────────┘     └─────────────┘
```

**Positive Cycle:**
1. Agent provides high-quality services, obtains successful transaction records
2. Credit score improves, tier rises
3. Can charge credit premium, obtain higher revenue
4. Can undertake higher-value tasks
5. Obtain more endorsements and validations, further improving credit

**Negative Cycle:**
1. Agent violates rules or provides low-quality services
2. Credit score decreases, tier drops
3. Stake slashed, economic loss
4. Can only undertake low-value tasks, revenue decreases
5. Principal marked, affecting other Agents

### 10.4 Credit Authority Economic Model

As credit issuing institutions, Credit Authorities also have corresponding economic incentives and constraints:

**Revenue Sources:**
- VC issuance fees (fixed fee per CreditVC)
- Subscription fees (Agent monthly/annual subscription to credit assessment services)
- Data API fees (third parties querying credit data)

**Constraint Mechanisms:**
- Credit Authorities need to stake a certain amount of Tokens
- If issued VCs are proven problematic (e.g., collusion fraud), stake will be slashed
- Continuously issuing low-quality VCs will result in removal from whitelist
- Forms a positive cycle of "reputation → business → revenue → higher reputation"

### 10.5 Token Economics (Optional)

The Agent-Score protocol itself does not mandate issuance of native Tokens, but is compatible with existing Token economies:

**Optional Token Uses:**
- Staking: Agents stake using native Tokens
- Payment: A2A transactions paid using native Tokens
- Governance: Token holders participate in Credit Authority whitelist voting
- Incentives: Reporting violations receives Token rewards

**Note:** M0-M3 phases do not depend on native Tokens, mainstream assets such as USDC and ETH can be used.

---

## Chapter 11: Security Analysis

### 11.1 Sybil Attack Resistance Analysis

Sybil attacks are one of the core challenges faced by decentralized credit systems. Agent-Score effectively resists Sybil attacks through multi-dimensional defense mechanisms:

**Defense Mechanism 1: Stake**
- Creating and maintaining Agents requires staking a certain amount of assets
- Attack cost = Number of Agents attacker wants to control × Minimum stake threshold
- Violations result in Slash, further increasing attack cost
- Economic analysis: If attack revenue < attack cost, attack is irrational

**Defense Mechanism 2: Principal Guarantee**
- Each Agent must be associated with a Principal
- Principal needs to pass KYB/KYC verification
- All Agents under the same Principal share a blacklist
- Attackers need a large number of real identities to create many Agents

**Defense Mechanism 3: Endorsement Diversity Detection**
- Jaccard cluster detection on endorsement graphs
- For clusters with similarity > 0.7, endorsement weights are halved
- Agents controlled by attackers endorsing each other will be detected

**Defense Mechanism 4: Device Binding**
- Each Agent needs to be bound to a physical device
- Device ID is guaranteed unique by TPM/TEE hardware
- Attackers need a large number of physical devices to create many Agents

**Comprehensive Analysis:**
- Attackers need to simultaneously break through four lines of defense: economic (Stake), identity (Principal), social (endorsement), hardware (device)
- Attack cost is much higher than potential revenue
- For most scenarios, dual-track system (Stake + Principal) meeting either provides sufficient Sybil resistance

### 11.2 Key Theft Resistance Analysis

Key theft is a core pain point in Agent security. Agent-Score effectively prevents key theft through device binding mechanisms:

**Attack Scenario 1: Key stolen, attacker uses on another device**
- Defense: Device binding VC contains device ID and hardware attestation
- Attacker's device does not have correct TPM/TEE attestation
- Device binding verification fails, handshake rejected
- Security Guarantee: ✅ Effectively defended

**Attack Scenario 2: Key stolen, attacker uses on the same device**
- Defense: Runtime binding requires continuous TEE verification
- If Agent runs in TEE, attacker cannot extract keys
- If device is stolen, Principal can remotely revoke device binding
- Security Guarantee: ✅ Effectively defended (strong binding level)

**Attack Scenario 3: Key stolen, attacker uses outside registration location**
- Defense: Network drift detection
- Attacker's IP prefix/ASN/country differs from registration
- Triggers drift detection, requires Principal co-signature
- Security Guarantee: ✅ Effectively defended

**Attack Scenario 4: Insider theft (legitimate device + legitimate network)**
- Defense: Principal co-signature requirement (high-security scenarios)
- Important operations require Principal secondary signature
- All operations have IPR records, traceable to specific operators
- Security Guarantee: ✅ Effectively defended (strong binding level)

### 11.3 Privacy Protection Analysis

Agent-Score fully considers privacy protection in design:

**Data Minimization Principle:**
- Network fingerprints only store IP prefixes (/24), no full IP addresses
- Use city-level geohash, no precise latitude/longitude storage
- IPR detailed data stored off-chain, only hashes anchored on-chain
- Support ZK selective disclosure, verify "credit score ≥ threshold" without exposing specific scores

**Identity Separation Design:**
- Agent DID separated from Principal DID, supporting controllable association
- Transaction records use pseudonyms, real identity only needs to be revealed during violation arbitration
- Support one-time transaction DIDs, protecting long-term identity privacy

**Compliance Considerations:**
- Data retention policy: IPR raw data retained for 2 years by default, violation records permanently retained
- Support "right to be forgotten": Non-essential data can be deleted after Agent deregistration
- Cross-regional data transmission complies with GDPR, CCPA, and other regulatory requirements

### 11.4 Smart Contract Security Considerations

**Reentrancy Attack Protection:**
- All external calls use "Check-Effects-Interactions" pattern
- Slash operations use Pull pattern, avoiding reentrancy risks
- Critical state changes use ReentrancyGuard

**Access Control:**
- Use multi-sig admin to manage Credit Authority whitelist
- Slash permission only granted to ViolationRegistry contract
- Support role permission separation (Owner, Admin, Operator)

**Upgradability Design:**
- Adopt Proxy / Diamond pattern, support contract upgrades
- Upgrades require multi-sig voting, preventing malicious upgrades
- Timelock required before upgrades, giving users sufficient time to react

---

## Chapter 12: Roadmap

### 12.1 Phase Planning

| Phase | Goal | Key Milestones | Timeline |
|---|---|---|---|
| **M0** | Protocol Specification | Complete SPEC document, JSON Schema, security audit | 2026 Q1 |
| **M1** | Contract Skeleton | ERC-8004 compatible registries, Stake/Violation Registry, Foundry tests | 2026 Q2 |
| **M2** | Credit Engine | FastAPI + LangGraph scoring pipeline, six-dimensional scoring model, CreditVC issuance | 2026 Q2 |
| **M3** | A2A Middleware | Python/TS SDK, handshake extension, device binding, FastAPI Adapter | 2026 Q3 |
| **M4** | ZK Privacy Layer | BBS+ VC, threshold proof circuits, ZK-SNARK integration | 2026 Q4 |
| **M5** | Testnet + Interoperability | Base Sepolia deployment, ERC-8004 interoperability testing, ecosystem integration | 2027 Q1 |
| **M6** | Mainnet Launch | Multi-chain deployment, DAO governance, ecosystem incentive program | 2027 Q2 |

### 12.2 Current Progress (v0.1.0)

✅ **Completed:**
- Complete protocol specification (§1-16)
- M1: Solidity registry contract skeletons (Identity, Reputation, Stake, Validation, Violation, CreditAuthority)
- M2: Credit Engine six-dimensional scoring model (Behavior, Stake, Endorsement, Validation, Device, Principal)
- M3: A2A Middleware handshake verification + policy engine
- M3.2: FastAPI HTTP Adapter
- M3.3: Device & Network Binding (TEE/TPM attestation + drift detection)
- JWS ES256K proof + alg/kid header validation
- Dual-signed IPR + on-chain anchoring abstraction
- Local MVP Demo + HTTP Demo + Minimal Demo
- Bilingual whitepaper (Chinese/English)
- Full test coverage (37 test cases, 100% pass rate)

⏳ **In Progress:**
- Foundry contract testing (requires local Foundry installation)
- Real TEE/TPM integration (currently Mock)
- Real IP/ASN/Geo database integration (currently Mock)

🔮 **Next Steps:**
- Deploy to Base Sepolia testnet
- Develop TypeScript SDK
- Integrate ZK selective disclosure
- Establish Credit Authority whitelist governance mechanism
- Ecosystem partner onboarding

### 12.3 Research Directions

**Long-term Research Topics:**
1. **Dynamic Weight Adjustment**: Automatically adjust scoring dimension weights based on market conditions
2. **Federated Learning Scoring**: Multi-party secure computation, joint modeling without disclosing raw data
3. **AI-driven Anomaly Detection**: Use LLM to analyze IPR content, detect fraud patterns
4. **Cross-chain Credit Migration**: Portability of Agent credit across different chains
5. **Post-quantum Secure Signatures**: Research and integration of post-quantum cryptography algorithms

---

## Chapter 13: Ecosystem

### 13.1 Partner Types

Agent-Score welcomes various ecosystem partners to join in building a trusted Agent ecosystem:

| Partner Type | Role | Collaboration Method |
|---|---|---|
| **Agent Platforms** | Provide Agent runtime environments | Integrate protocol SDK, provide credit scoring services |
| **Credit Authorities** | Issue CreditVC | Join whitelist, provide credit assessment services |
| **Device Authorities** | Issue DeviceBindingVC | Verify TEE/TPM attestations, provide device identity services |
| **Validators** | Provide third-party validation | zkML, TEE, re-execution and other validation services |
| **Wallet Providers** | Manage Agent keys | Integrate DID management, support device binding |
| **Application Developers** | Build Agent applications | Use protocol for trusted A2A interactions |

### 13.2 Developer Support

- **Documentation Center**: Complete API documentation, tutorials, best practices
- **SDKs**: Python, TypeScript, Rust multi-language SDKs
- **Testnet**: Free testnet environment, provides test Tokens
- **Developer Community**: Discord, GitHub Discussions, monthly developer calls
- **Grant Program**: Ecosystem project grants, hackathon prizes

---

## References

### Standards and Specifications

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

### Related Technologies

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

### Related Projects

11. **MolTrust IPR** - Interaction Proof Record for Agent Trust  
    https://github.com/moltrust/ipr-spec

12. **ACTA** - Agent Credential Trust Architecture  
    https://github.com/acta-protocol/acta-spec

13. **qntm Authority** - Decentralized Agent Authority  
    https://github.com/qntm-network/authority-spec

### Security Research

14. **Sybil Attacks in Decentralized Systems**  
    Douceur, J. R. (2002). The Sybil Attack. IPTPS.

15. **JWS Algorithm Downgrade Attacks**  
    https://auth0.com/blog/critical-vulnerabilities-in-json-web-token-libraries/

16. **TPM 2.0 Security Best Practices**  
    https://trustedcomputinggroup.org/wp-content/uploads/TPM-2.0-Security-Best-Practices.pdf

---

## Appendix

### A. Glossary

| Term | Definition |
|---|---|
| **Agent** | Autonomous entity driven by LLM/workflow |
| **Principal** | Responsible party behind an Agent (natural person/legal entity/DAO) |
| **DID** | Decentralized Identifier |
| **VC** | Verifiable Credential |
| **CreditVC** | Credit Verifiable Credential, containing Agent credit score |
| **DeviceBindingVC** | Device Binding Verifiable Credential, proving Agent runs on trusted device |
| **IPR** | Interaction Proof Record, dual-signed evidence of A2A transaction |
| **TEE** | Trusted Execution Environment |
| **TPM** | Trusted Platform Module |
| **Sybil Attack** | Attack by creating large number of fake identities |
| **Sybil Resistance** | Mechanism to prevent Sybil attacks |

### B. Scoring Parameter Reference

| Parameter | Default Value | Description |
|---|---:|---|
| Base Score | 300 | Initial score for new Agents |
| Behavior Weight | 350 | Historical behavior dimension weight |
| Endorsement Weight | 150 | Cross-domain endorsement dimension weight |
| Stake Weight | 200 | Stake dimension weight |
| Validation Weight | 150 | Third-party validation dimension weight |
| Device Weight | 100 | Device binding dimension weight |
| Principal Weight | 50 | Principal credit dimension weight |
| Violation Penalty Coefficient λ | 400 | Violation penalty coefficient |
| Time Decay τ | 180 days | Time decay constant for violation records |
| CreditVC Validity | 30 days | Validity period of credit credential |
| DeviceBindingVC Validity | 24 hours | Validity period of device binding credential |
| Jaccard Similarity Threshold | 0.7 | Endorsement cluster detection threshold |
| Asset Concentration Threshold | 80% | Single asset stake ratio threshold |

### C. Contact Information

- **Website**: https://agent-score.org
- **GitHub**: https://github.com/agent-score/agent-score
- **Discord**: https://discord.gg/agent-score
- **Twitter/X**: @AgentScoreOrg
- **Email**: contact@agent-score.org

---

**Document Version:** v0.1.0-draft  
**Last Updated:** 2026-05-28  
**Copyright:** © 2026 Agent-Score Contributors. Licensed under MIT.