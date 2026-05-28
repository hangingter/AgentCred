# M2 Credit Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the deterministic off-chain credit scoring core for Agent-Score.

**Architecture:** Keep scoring as a pure Python library with dataclass inputs and deterministic outputs. Chain adapters, FastAPI routes, and CreditVC signing must wrap this core instead of embedding scoring logic. The current implementation covers M2 core scoring; API and VC signing are the next sub-tasks.

**Tech Stack:** Python 3.11+, stdlib dataclasses, unittest, optional FastAPI dependency for later API wrapping.

---

### Task 1: Package Skeleton

**Files:**
- Create: `credit-engine/pyproject.toml`
- Create: `credit-engine/agent_score_engine/__init__.py`

- [x] Define `agent-score-engine` package with no mandatory runtime dependencies.
- [x] Add optional extras for `api` and `dev`.
- [x] Export public scoring models and `calculate_credit_score`.

### Task 2: Scoring Data Models

**Files:**
- Create: `credit-engine/agent_score_engine/models.py`

- [x] Define `InteractionProofRecord` with dual-signature coverage.
- [x] Define `StakeSnapshot` with `usd_value`, `weight`, and `lock_days_remaining`.
- [x] Define `ViolationEvent` with severity validation in `[0, 100]`.
- [x] Define `EndorsementEdge`, `ValidationAttestation`, and `PrincipalProfile`.
- [x] Define `CreditInput`, `DimensionScores`, and `CreditResult`.

### Task 3: Deterministic Scoring Engine

**Files:**
- Create: `credit-engine/agent_score_engine/scoring.py`

- [x] Implement BehaviorScore with Bayesian smoothing and repeat-client rate.
- [x] Implement StakeScore with multi-asset USD totals, lock multiplier, and concentration penalty.
- [x] Implement EndorsementScore with cluster concentration risk.
- [x] Implement ValidationScore with `tee`, `re_execution`, and `zkml` weights.
- [x] Implement PrincipalScore as `principal_score / 1000 * 100 * 0.3`.
- [x] Implement ViolationPenalty with 180-day exponential decay.
- [x] Emit reason codes for low sample, low stake, concentration, violations, cluster risk, validation coverage, and expired principal VC.

### Task 4: Core Tests

**Files:**
- Create: `credit-engine/tests/test_scoring.py`

- [x] Test strong agent reaches S tier without reason codes.
- [x] Test low sample and low stake emit reason codes.
- [x] Test stake concentration reduces stake dimension.
- [x] Test critical principal violation caps score to C tier.
- [x] Test recent violations apply decay penalty and emit violation reason codes.

### Task 5: Verification

**Commands:**
- `cd /Users/bytedance/code/agent-score/credit-engine`
- `python3 -m unittest discover -s tests -v`

**Result:**
- [x] 5 tests passed.

### Task 6: CreditVC, Schema, And API Wrapper

**Files:**
- Create: `credit-engine/agent_score_engine/vc.py`
- Create: `credit-engine/agent_score_engine/schemas.py`
- Create: `credit-engine/api/main.py`
- Create: `credit-engine/tests/test_vc.py`
- Create: `credit-engine/tests/test_api.py`

- [x] Add deterministic CreditVC payload builder with 30-day validity.
- [x] Add issuer whitelist verification hook.
- [x] Add FastAPI `/score` endpoint that accepts `CreditInput` JSON and returns `CreditResult`.
- [x] Add FastAPI `/issue-vc` endpoint that signs a VC-like payload with a configured authority key.
- [x] Add JSON schema export for `InteractionProofRecord`, `StakeSnapshot`, `ViolationEvent`, and `CreditVC`.
- [x] Add tests for VC building, signature verification, expiry rejection, tamper rejection, `/score`, `/issue-vc`, and missing authority secret.
- [x] Verify with `python3 -m unittest discover -s tests -v`: 12 tests passed.
