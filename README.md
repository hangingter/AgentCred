<p align="center">
  <img src="docs/assets/agentcred-readme-cover.png" alt="AgentCred README cover" width="100%" />
</p>

# AgentCred 智信护照

> Banking-grade credit passport and trust protocol for AI Agents.

Formerly **Agent-Score**: a decentralized credit protocol for AI Agents, providing banking-grade identity verification, credit scoring, and accountability. It achieves a complete trust chain: **Agent → Device → Owner**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![ERC-8004](https://img.shields.io/badge/ERC--8004-compatible-green.svg)](https://eips.ethereum.org/EIPS/eip-8004)
[![Google A2A](https://img.shields.io/badge/Google%20A2A-compatible-blue.svg)](https://github.com/google/a2a-protocol)

---

## 📚 Whitepapers

| Language | Link |
|---|---|
| 🇨🇳 中文 | [docs/whitepaper/whitepaper-CN.md](docs/whitepaper/whitepaper-CN.md) |
| 🇺🇸 English | [docs/whitepaper/whitepaper-EN.md](docs/whitepaper/whitepaper-EN.md) |

## 🔎 Architecture Review

| Document | Description |
|---|---|
| [AgentCred Architecture Review CN](docs/reviews/2026-06-01-agentcred-architecture-review-cn.md) | One-page risk and architecture review for MVP readiness, trust roots, interoperability, and production gaps |

---

## ✨ Core Features

### 🔐 Identity & Security
- **DID Identity**: W3C DID-compatible agent identity (`did:ethr:`)
- **Principal Association**: Every agent is linked to a responsible party (person/entity/DAO)
- **Device Binding**: TEE/TPM hardware attestation prevents key theft
- **Network Fingerprinting**: IP prefix, ASN, country code for drift detection
- **JWS Security**: ES256K signatures with `alg`/`kid` header validation

### 📊 Credit Scoring
- **Six-Dimensional Model**: Behavior, Stake, Endorsement, Validation, Device, Principal
- **Reason Codes**: Bank-level interpretability for every score
- **CreditVC**: 30-day verifiable credentials
- **Tier System**: S (900-1000) → A → B → C → D (0-399)

### 🤝 Trust Handshake
- **< 100ms Verification**: Fast authentication before A2A calls
- **Flexible Policy Engine**: Configurable thresholds for credit, tier, device binding
- **Dual-Signed IPR**: Non-repudiable interaction records
- **Chain Anchoring**: Merkle root anchoring for immutable evidence

### 🛡️ Sybil Resistance
- **Dual-Track System**: Stake + Principal guarantee
- **Endorsement Diversity**: Jaccard cluster detection prevents mutual admiration rings
- **Device Uniqueness**: Hardware-bound identities

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│  L5  Application       Business Agents (LangGraph / CrewAI) │
├──────────────────────────────────────────────────────────┤
│  L4  Communication     Google A2A v1.0 (Agent Card, JSON-RPC)│
├──────────────────────────────────────────────────────────┤
│  L3  Trust Handshake   Agent-Score Handshake Extension     │
├──────────────────────────────────────────────────────────┤
│  L2  Credit Engine     Scoring Model + VC Issuance         │
├──────────────────────────────────────────────────────────┤
│  L1  Registries        Identity / Reputation / Stake       │
│                        / Validation / Violation            │
├──────────────────────────────────────────────────────────┤
│  L0  Settlement        EVM L2 (Base / OP / Arbitrum)       │
└──────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
agent-score/
├── docs/
│   ├── whitepaper/           # Bilingual whitepapers
│   │   ├── whitepaper-CN.md  # 中文白皮书
│   │   └── whitepaper-EN.md  # English whitepaper
│   ├── protocol/
│   │   └── SPEC.md           # Full protocol specification
│   ├── designs/              # Design documents
│   └── superpowers/plans/    # Implementation plans
├── src/
│   ├── contracts/            # Solidity M1 registry contracts
│   │   ├── interfaces/
│   │   ├── registries/
│   │   ├── AgentScoreTypes.sol
│   │   └── Ownable.sol
│   ├── credit-engine/        # Python credit engine package
│   │   ├── agent_score_engine/
│   │   ├── api/
│   │   └── tests/
│   └── a2a-middleware/       # Python A2A middleware package
│       ├── agent_score_middleware/
│       └── tests/
├── demos/
│   ├── minimal/              # Quick start demos
│   │   ├── 1_declare_agent.py
│   │   └── 2_trade_with_protocol.py
│   ├── mvp/                  # Full protocol simulation
│   │   ├── agents.py
│   │   ├── demo.py
│   │   ├── protocol.py
│   │   └── tests/
│   └── http/                 # FastAPI A2A integration
│       ├── demo.py
│       └── tests/
├── script/                   # Foundry deploy scripts
├── test/                     # Foundry tests
├── examples/                 # Usage examples
├── .github/                  # GitHub configuration
├── LICENSE                   # MIT License
├── README.md                 # This file
├── CHANGELOG.md              # Change log
├── CONTRIBUTING.md           # Contribution guidelines
├── pyproject.toml            # Python project configuration
├── foundry.toml              # Foundry configuration
└── .gitignore                # Git ignore rules
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.7.17+ (due to environment constraints)
- Foundry (for Solidity contract testing)

### 1. Clone and Setup

```bash
git clone https://github.com/agent-score/agent-score.git
cd agent-score

# Set up Python environment
python3.7 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### 2. Run Minimal Demo

```bash
# Demo 1: Declare your agent identity
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http \
  python3 demos/minimal/1_declare_agent.py

# Demo 2: Two-party trusted trading
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http \
  python3 demos/minimal/2_trade_with_protocol.py
```

### 3. Run Full Test Suite

```bash
# Credit Engine tests (16 tests)
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http \
  python3 -m unittest discover -s src/credit-engine/tests -v

# A2A Middleware tests (16 tests)
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http \
  python3 -m unittest discover -s src/a2a-middleware/tests -v

# MVP Demo tests (4 tests)
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http \
  python3 -m unittest discover -s demos/mvp/tests -v

# HTTP Demo tests (1 test)
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http \
  python3 -m unittest discover -s demos/http/tests -v
```

**Expected Result:**
```
credit-engine: Ran 16 tests OK
a2a-middleware: Ran 16 tests OK
demos/mvp: Ran 4 tests OK
demos/http: Ran 1 test OK
```

### 4. Run HTTP Demo

```bash
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http \
  python3 demos/http/demo.py
```

---

## 📖 Documentation

| Document | Description |
|---|---|
| [Protocol Spec](docs/protocol/SPEC.md) | Complete protocol specification (§1-16) |
| [Device Binding Design](docs/designs/2026-05-28-device-network-binding-design.md) | Device & network binding design document |
| [API Reference](https://docs.agent-score.org/api) | Full API documentation |
| [Contributing Guide](CONTRIBUTING.md) | How to contribute to the project |
| [Changelog](CHANGELOG.md) | Release notes and changes |

---

## 🧪 Test Coverage

| Module | Tests | Status |
|---|---:|---|
| Credit Engine | 16 | ✅ |
| A2A Middleware | 16 | ✅ |
| MVP Demo | 4 | ✅ |
| HTTP Demo | 1 | ✅ |
| **Total** | **37** | **✅ 100%** |

---

## 🛡️ Security

### Security Features
- ✅ JWS header validation (`alg=ES256K`, `kid=issuer`) prevents algorithm downgrade
- ✅ Device binding prevents key theft across devices
- ✅ Network drift detection identifies unauthorized location changes
- ✅ Principal association ensures accountability for violations
- ✅ Dual signature mechanism prevents transaction repudiation
- ✅ Violation records bound to Principal, persistent across Agents

### Reporting Vulnerabilities

> **Never report security related issues, vulnerabilities or bugs including sensitive information to the issue tracker, or elsewhere in public.**

Instead, sensitive bugs must be sent by email to <security@agent-score.org>.

---

## 🤝 Contributing

We welcome all types of contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Ways to Contribute
- 🐛 Report bugs
- 💡 Suggest enhancements
- 📝 Improve documentation
- 💻 Submit code changes
- 🌐 Translate documentation

### Development Workflow
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'feat: add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌐 Community

- **Website**: [agent-score.org](https://agent-score.org)
- **GitHub**: [github.com/agent-score/agent-score](https://github.com/agent-score/agent-score)
- **Discord**: [discord.gg/agent-score](https://discord.gg/agent-score)
- **Twitter/X**: [@AgentScoreOrg](https://twitter.com/AgentScoreOrg)
- **Email**: [team@agent-score.org](mailto:team@agent-score.org)

---

## 🗺️ Roadmap

| Phase | Goal | Status |
|---|---|---|
| **M0** | Protocol Specification | ✅ Done |
| **M1** | Contract Skeleton | ✅ Done (tests pending Foundry install) |
| **M2** | Credit Engine | ✅ Done |
| **M3** | A2A Middleware | ✅ Done |
| **M3.2** | HTTP Adapter | ✅ Done |
| **M3.3** | Device Binding | ✅ Done |
| **M4** | ZK Privacy Layer | ⏳ In Progress |
| **M5** | Testnet + Interoperability | 🔮 Next |
| **M6** | Mainnet Launch | 🔮 Future |

---

## 🙏 Acknowledgments

This project builds upon excellent work from:
- [W3C DID Working Group](https://www.w3.org/groups/wg/did)
- [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) authors
- [Google A2A Protocol](https://github.com/google/a2a-protocol) team
- [MolTrust IPR](https://github.com/moltrust/ipr-spec) project
- [ACTA](https://github.com/acta-protocol/acta-spec) protocol

---

**Built with ❤️ for the AI Agent ecosystem**
