# M1 Foundry Registries Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the M1 on-chain Registry foundation for Agent-Score.

**Architecture:** Use a dependency-light Foundry project. Keep identity, authority, stake, reputation, validation, and violation responsibilities split across focused contracts. Keep credit scoring off-chain; contracts only store identity, anchors, stake positions, authority whitelist, and principal-linked violation evidence.

**Tech Stack:** Solidity 0.8.24, Foundry, no external Solidity dependencies for M1.

---

### Task 1: Foundry Project Skeleton

**Files:**
- Create: `foundry.toml`
- Create directories: `src/`, `src/interfaces/`, `src/registries/`, `test/`, `script/`

- [x] Create the Foundry configuration with Solidity 0.8.24, optimizer enabled, and standard `src/test/script` paths.
- [x] Avoid external dependencies so `forge test` can run before installing `openzeppelin` or `forge-std`.

### Task 2: Shared Types And Ownership

**Files:**
- Create: `src/AgentScoreTypes.sol`
- Create: `src/Ownable.sol`
- Create: `src/interfaces/IAgentIdentityRegistry.sol`
- Create: `src/interfaces/IERC20.sol`

- [x] Add shared structs for agent records, stake positions, and authorities.
- [x] Add minimal owner access control for admin-gated registries.
- [x] Add small interfaces used by registries without importing third-party code.

### Task 3: M1 Registries

**Files:**
- Create: `src/registries/IdentityRegistry.sol`
- Create: `src/registries/CreditAuthorityRegistry.sol`
- Create: `src/registries/StakeRegistry.sol`
- Create: `src/registries/ReputationRegistry.sol`
- Create: `src/registries/ValidationRegistry.sol`
- Create: `src/registries/ViolationRegistry.sol`

- [x] Implement ERC-8004-compatible identity semantics with non-transferable agent passports.
- [x] Implement Credit Authority whitelist add/remove lifecycle.
- [x] Implement multi-asset staking for ERC20 and native ETH.
- [x] Implement IPR root anchoring for reputation.
- [x] Implement validation attestation anchoring.
- [x] Implement principal-linked violation records with severity 0–100.

### Task 4: Deployment And Tests

**Files:**
- Create: `script/DeployM1.s.sol`
- Create: `test/M1Registries.t.sol`

- [x] Add a dependency-free deployment helper for all M1 registries.
- [x] Add Solidity tests for registration, authority whitelist, ERC20 staking/slashing, IPR anchoring, validation anchoring, and violation recording.

### Task 5: Verification

**Commands:**
- `forge fmt`
- `forge test`

- [ ] Run after installing Foundry locally. Current machine returned `forge: command not found`, so tests are written but not executed in this session.
