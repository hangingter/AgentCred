# Project Reorganization & Whitepaper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the agent-score project into a standard Git repository structure, update documentation, and create bilingual (Chinese/English) whitepapers.

**Architecture:** Follow standard open-source project conventions with clear separation of concerns: contracts, Python packages, demos, docs, and tests at appropriate levels.

**Tech Stack:** Python 3.7+, Solidity (Foundry), Markdown documentation

---

## File Structure

### New Standard Layout

```
agent-score/
├── .github/
│   └── workflows/
│       └── ci.yml                          # CI workflow (optional)
├── docs/
│   ├── whitepaper/
│   │   ├── whitepaper-CN.md                # Chinese whitepaper
│   │   └── whitepaper-EN.md                # English whitepaper
│   ├── protocol/
│   │   └── SPEC.md                         # Protocol specification
│   ├── designs/
│   │   └── 2026-05-28-device-network-binding-design.md
│   └── plans/
│       └── *.md                            # Implementation plans
├── src/
│   ├── contracts/                          # Solidity contracts (moved from src/)
│   │   ├── AgentScoreTypes.sol
│   │   ├── Ownable.sol
│   │   ├── interfaces/
│   │   └── registries/
│   ├── credit-engine/                      # Python credit engine package
│   │   ├── agent_score_engine/
│   │   ├── api/
│   │   ├── tests/
│   │   └── pyproject.toml
│   └── a2a-middleware/                     # Python A2A middleware package
│       ├── agent_score_middleware/
│       └── tests/
├── demos/
│   ├── minimal/                            # Moved from minimal-demo/
│   │   ├── 1_declare_agent.py
│   │   ├── 2_trade_with_protocol.py
│   │   └── README.md
│   ├── mvp/                                # Moved from mvp-demo/
│   │   ├── agents.py
│   │   ├── demo.py
│   │   ├── protocol.py
│   │   └── tests/
│   └── http/                               # Moved from http-demo/
│       ├── demo.py
│       └── tests/
├── script/
│   └── DeployM1.s.sol
├── test/
│   └── M1Registries.t.sol
├── examples/
│   └── README.md                           # Usage examples
├── README.md                               # Updated project README
├── CONTRIBUTING.md                         # Contribution guidelines
├── CHANGELOG.md                            # Change log
├── LICENSE                                 # License file
├── pyproject.toml                          # Root Python project config
├── foundry.toml                            # Foundry config
└── .gitignore                              # Git ignore rules
```

### Files to Create

1. `docs/whitepaper/whitepaper-CN.md` - Chinese whitepaper (~5000 words)
2. `docs/whitepaper/whitepaper-EN.md` - English whitepaper (~5000 words)
3. `CONTRIBUTING.md` - Contribution guidelines
4. `CHANGELOG.md` - Change log with initial release
5. `LICENSE` - MIT or Apache 2.0 license
6. `pyproject.toml` - Root Python project configuration
7. `.gitignore` - Git ignore rules
8. `examples/README.md` - Examples directory placeholder

### Files to Move

1. `src/` → `src/contracts/` (Solidity contracts)
2. `minimal-demo/` → `demos/minimal/`
3. `mvp-demo/` → `demos/mvp/`
4. `http-demo/` → `demos/http/`
5. `protocol/SPEC.md` → `docs/protocol/SPEC.md`
6. `docs/superpowers/specs/` → `docs/designs/`

### Files to Update

1. `README.md` - Update with new structure, links to whitepaper
2. All Python import paths in moved files

---

## Task 1: Create Whitepaper (Chinese)

**Files:**
- Create: `docs/whitepaper/whitepaper-CN.md`

**Whitepaper Structure:**

1. **摘要 / Executive Summary**
   - 项目背景：Agent 生态的信任问题
   - 解决方案：Agent-Score 信用协议
   - 核心创新：DID + VC + 设备绑定 + 信用评分

2. **第一章：引言 / Introduction**
   - AI Agent 的爆发与信任缺口
   - 现有方案的局限性（纯声誉、无硬件绑定）
   - Agent-Score 的使命：构建银行级 Agent 信用体系

3. **第二章：设计原则 / Design Principles**
   - 不重造轮子：复用 W3C DID/VC、ERC-8004、Google A2A
   - 链上轻、链下重：链上锚定，链下计算
   - 隐私优先：ZK 选择性披露
   - Sybil 抵抗双轨制：Stake + Principal 担保
   - 可问责：每笔交易可回溯到 Principal

4. **第三章：系统架构 / System Architecture**
   - 五层架构：L0 结算层 → L1 注册表 → L2 信用引擎 → L3 握手层 → L4 通信层 → L5 应用层
   - 核心组件：Identity Registry、Credit Engine、A2A Middleware
   - 协议流程：身份声明 → 信用评估 → 握手验证 → 交易执行 → 存证结算

5. **第四章：身份层 / Identity Layer**
   - DID Method：`did:ethr:` 设计决策
   - Agent Passport：ERC-721 Soulbound Token
   - Principal 关联：Agent → 责任主体映射
   - 设备绑定：TEE/TPM 硬件证明，防止密钥盗用

6. **第五章：信用引擎 / Credit Engine**
   - 六维评分模型：行为、质押、背书、验证、设备、主体
   - 评分公式与权重分配
   - CreditVC：30 天可验证信用凭证
   - Reason Code：可解释性原因码

7. **第六章：设备与网络绑定 / Device & Network Binding**
   - 绑定级别：none → registration → runtime → strong
   - 设备证明：TPM Quote / TEE Report
   - 网络指纹：IP 前缀、ASN、国家代码
   - 漂移检测：异常位置识别与 Principal 副署机制

8. **第七章：快速认证层 / Trust Handshake Layer**
   - 握手流程：6 步快速认证（< 100ms）
   - 策略引擎：可配置的信任门槛
   - JWS 验证：alg=ES256K + kid 校验，防算法降级

9. **第八章：交互存证 / Interaction Proof Record**
   - IPR 数据结构：双签防抵赖
   - 链上锚定：Merkle Root 上链
   - 信用激励：成功交易提升信用分

10. **第九章：注册表合约 / Registry Contracts**
    - Identity Registry：Agent 身份注册
    - Stake Registry：多资产质押与 Slash
    - Violation Registry：违规记录绑定 Principal
    - Credit Authority Registry：白名单制权威机构

11. **第十章：经济模型 / Economic Model**
    - 信用溢价：高信用 Agent 获得更高调用价格
    - 惩罚机制：违规 Slash + 等级降级
    - 激励闭环：交易 → 信用 → 更高收益

12. **第十一章：安全分析 / Security Analysis**
    - 抗 Sybil 攻击分析
    - 抗密钥盗用分析
    - 隐私保护分析
    - 智能合约安全考虑

13. **第十二章：路线图 / Roadmap**
    - M0-M5 阶段规划
    - 当前进展与下一步

14. **参考文献 / References**
    - W3C DID/VC、ERC-8004、Google A2A 等

- [ ] **Step 1: Write Chinese whitepaper content**

Create the full whitepaper in Chinese following the structure above.

- [ ] **Step 2: Verify whitepaper completeness**

Ensure all sections are covered and the content is technically accurate.

---

## Task 2: Create Whitepaper (English)

**Files:**
- Create: `docs/whitepaper/whitepaper-EN.md`

- [ ] **Step 1: Translate whitepaper to English**

Translate the complete Chinese whitepaper to English, maintaining technical accuracy and professional tone.

- [ ] **Step 2: Verify English translation**

Ensure terminology is consistent (DID, VC, Sybil, etc.) and the translation is natural.

---

## Task 3: Reorganize Project Structure

**Files:**
- Move: `src/` → `src/contracts/`
- Move: `minimal-demo/` → `demos/minimal/`
- Move: `mvp-demo/` → `demos/mvp/`
- Move: `http-demo/` → `demos/http/`
- Move: `protocol/SPEC.md` → `docs/protocol/SPEC.md`
- Move: `docs/superpowers/specs/` → `docs/designs/`

- [ ] **Step 1: Move Solidity contracts to src/contracts/**

```bash
mkdir -p src/contracts
mv src/AgentScoreTypes.sol src/Ownable.sol src/contracts/
mv src/interfaces src/registries src/contracts/
```

- [ ] **Step 2: Move demos to demos/ directory**

```bash
mkdir -p demos
mv minimal-demo demos/minimal
mv mvp-demo demos/mvp
mv http-demo demos/http
```

- [ ] **Step 3: Move protocol spec to docs/protocol/**

```bash
mkdir -p docs/protocol
mv protocol/SPEC.md docs/protocol/
rmdir protocol
```

- [ ] **Step 4: Move design specs to docs/designs/**

```bash
mkdir -p docs/designs
mv docs/superpowers/specs/* docs/designs/
```

- [ ] **Step 5: Update import paths in demo files**

Update all Python import paths in moved demo files to reflect new directory structure.

---

## Task 4: Create Standard Project Files

**Files:**
- Create: `LICENSE` (MIT License)
- Create: `CONTRIBUTING.md`
- Create: `CHANGELOG.md`
- Create: `pyproject.toml` (root)
- Create: `.gitignore`
- Create: `examples/README.md`

- [ ] **Step 1: Create LICENSE file**

```text
MIT License

Copyright (c) 2026 Agent-Score Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Create CONTRIBUTING.md**

Create contribution guidelines including:
- Code of Conduct
- How to report bugs
- How to submit feature requests
- Development setup
- Pull request process
- Coding standards

- [ ] **Step 3: Create CHANGELOG.md**

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-05-28

### Added
- Initial protocol specification (§1-16)
- M1: Solidity registry contracts (Identity, Reputation, Stake, Validation, Violation, CreditAuthority)
- M2: Credit Engine with 6-dimensional scoring (behavior, stake, endorsement, validation, device, principal)
- M3: A2A Middleware with trust handshake and policy engine
- M3.2: FastAPI HTTP adapter for A2A endpoints
- M3.3: Device & Network Binding with TEE/TPM attestation and drift detection
- JWS ES256K proof with alg/kid header validation
- Dual-signed IPR (Interaction Proof Record) with chain anchoring
- Local MVP demo and HTTP demo
- Minimal demos for agent declaration and trading
- Bilingual whitepaper (Chinese/English)
```

- [ ] **Step 4: Create root pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "agent-score"
version = "0.1.0"
description = "A2A trust protocol for agent identity, credit scoring, and accountability"
readme = "README.md"
requires-python = ">=3.7"
license = {text = "MIT"}
authors = [{name = "Agent-Score Contributors"}]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
dependencies = [
    "pydantic>=1.10,<2.0",
    "fastapi>=0.95",
    "uvicorn>=0.22",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "httpx>=0.24",
]

[tool.setuptools.packages.find]
where = ["src/credit-engine", "src/a2a-middleware"]
```

- [ ] **Step 5: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
.coverage
htmlcov/

# Foundry
cache/
out/

# Environment
.env
.env.local
```

- [ ] **Step 6: Create examples/README.md**

```markdown
# Examples

This directory contains usage examples for the Agent-Score protocol.

## Available Examples

- **[Minimal Demo](../demos/minimal/)**: Quick start guide for agent declaration and trading
- **[MVP Demo](../demos/mvp/)**: Full protocol simulation with local agents
- **[HTTP Demo](../demos/http/)**: HTTP A2A integration with FastAPI

## Coming Soon

- Real blockchain integration example
- Multi-agent orchestration example
- ZK selective disclosure example
```

---

## Task 5: Update README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README with new structure**

Update the README to include:
- New project structure overview
- Links to whitepaper (CN/EN)
- Links to protocol spec
- Updated demo paths
- Quick start guide
- Contribution link
- License information

---

## Task 6: Verify Project Structure

**Files:**
- All files

- [ ] **Step 1: Run full test suite**

```bash
cd /Users/bytedance/code/agent-score
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http python3 -m unittest discover -s src/credit-engine/tests -v
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http python3 -m unittest discover -s src/a2a-middleware/tests -v
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http python3 -m unittest discover -s demos/mvp/tests -v
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http python3 -m unittest discover -s demos/http/tests -v
```

- [ ] **Step 2: Run minimal demos**

```bash
cd /Users/bytedance/code/agent-score
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http python3 demos/minimal/1_declare_agent.py
PYTHONPATH=src/credit-engine:src/a2a-middleware:demos/mvp:demos/minimal:demos/http python3 demos/minimal/2_trade_with_protocol.py
```

- [ ] **Step 3: Verify all files are in correct locations**

Check that all moved files exist in their new locations and no broken references remain.

---

## Self-Review

**1. Spec coverage:**
- ✅ Project reorganization into standard Git structure
- ✅ Bilingual whitepaper (CN/EN) with all 14 sections
- ✅ Standard project files (LICENSE, CONTRIBUTING, CHANGELOG, etc.)
- ✅ Updated README with new structure
- ✅ Verification of all tests passing

**2. Placeholder scan:**
- No TBD/TODO placeholders
- All code blocks contain actual content
- All commands are specific and executable

**3. Type consistency:**
- File paths are consistent across all tasks
- Import path updates are accounted for
- Demo run commands reflect new directory structure

Plan complete and saved to `docs/superpowers/plans/2026-05-28-project-reorganization-whitepaper.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
