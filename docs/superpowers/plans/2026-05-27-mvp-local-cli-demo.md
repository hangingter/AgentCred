# MVP Local CLI Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a one-command MVP that demonstrates the complete Agent-Score protocol loop.

**Architecture:** Implement a local, single-process CLI demo under `mvp-demo/`. It reuses `credit-engine` for scoring and CreditVC verification, simulates Agent Cards, A2A handshake, policy checks, task execution, dual-signed IPR generation, and score refresh. It avoids live chain/RPC dependencies; M1 contracts remain the future persistence layer.

**Tech Stack:** Python 3.9+, stdlib dataclasses/hashlib/json/hmac, existing `credit-engine` package.

---

### Task 1: Protocol Models And Policy Checks

**Files:**
- Create: `mvp-demo/protocol.py`

- [x] Define `AgentPolicy`, `AgentCard`, `HandshakeResult`, and `InteractionProofRecordEnvelope`.
- [x] Implement `verify_agent_card_credit()` using `verify_credit_vc()`.
- [x] Enforce `min_credit_score`, `min_tier`, trusted issuer, expiry, signature, and max violation count.

### Task 2: Local Agent Simulation

**Files:**
- Create: `mvp-demo/agents.py`

- [x] Define `LocalAgent` with DID, principal DID, policy, initial credit input, and secret.
- [x] Implement `agent_card()` that embeds `x-agent-score` with a signed CreditVC.
- [x] Implement `handle_task()` that returns a deterministic task result.
- [x] Implement `build_ipr()` that creates a dual-signed interaction proof envelope.

### Task 3: CLI Demo

**Files:**
- Create: `mvp-demo/demo.py`

- [x] Instantiate a trusted Credit Authority and two agents.
- [x] Print Provider Agent Card.
- [x] Perform A2A-style handshake and print policy decision.
- [x] Execute one task and print task result.
- [x] Build IPR envelope and print IPR hash.
- [x] Recalculate provider score with the new IPR sample and print score delta.

### Task 4: Tests

**Files:**
- Create: `mvp-demo/tests/test_mvp_demo.py`

- [x] Test a valid provider passes handshake.
- [x] Test an untrusted issuer fails handshake.
- [x] Test a score below policy threshold fails handshake.
- [x] Test demo run returns IPR hash and updated score.

### Task 5: Verification

**Commands:**
- `cd /Users/bytedance/code/agent-score`
- `PYTHONPATH=credit-engine:mvp-demo python3 -m unittest discover -s mvp-demo/tests -v`
- `PYTHONPATH=credit-engine:mvp-demo python3 mvp-demo/demo.py`

- [x] All MVP tests pass.
- [x] Demo prints Agent Card, handshake, task result, IPR hash, and score delta.
