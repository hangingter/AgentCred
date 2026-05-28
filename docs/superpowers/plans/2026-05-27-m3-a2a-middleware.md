# M3 A2A Middleware Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract the MVP trust handshake into a reusable Python `a2a-middleware` package.

**Architecture:** Keep M3 library-first. The middleware package owns Agent Card parsing, policy checks, CreditVC verification, lightweight payload signing, and IPR envelope construction. The MVP demo becomes a consumer of this package instead of owning protocol logic. HTTP/FastAPI adapters are deferred to the next increment.

**Tech Stack:** Python 3.9+, stdlib dataclasses/json/hashlib/hmac, existing `credit-engine` package.

---

### Task 1: Package Skeleton

**Files:**
- Create: `a2a-middleware/agent_score_middleware/__init__.py`
- Create: `a2a-middleware/agent_score_middleware/models.py`
- Create: `a2a-middleware/agent_score_middleware/handshake.py`
- Create: `a2a-middleware/agent_score_middleware/ipr.py`
- Create: `a2a-middleware/tests/test_middleware.py`

- [x] Create a reusable middleware package with no required web framework.

### Task 2: Models

**Files:**
- Create: `a2a-middleware/agent_score_middleware/models.py`

- [x] Move `AgentPolicy`, `AgentCard`, `HandshakeResult`, and `InteractionProofRecordEnvelope` from `mvp-demo/protocol.py`.
- [x] Preserve A2A-compatible `AgentCard.to_a2a_dict()`.

### Task 3: Handshake And IPR Helpers

**Files:**
- Create: `a2a-middleware/agent_score_middleware/handshake.py`
- Create: `a2a-middleware/agent_score_middleware/ipr.py`

- [x] Move `verify_agent_card_credit()` into `handshake.py`.
- [x] Move `sign_payload()` and `sha256_json()` into `ipr.py`.

### Task 4: Demo Refactor

**Files:**
- Modify: `mvp-demo/protocol.py`
- Modify: `mvp-demo/agents.py`
- Modify: `mvp-demo/demo.py`
- Modify: `mvp-demo/tests/test_mvp_demo.py`

- [x] Re-export middleware symbols from `mvp-demo/protocol.py` for backward compatibility.
- [x] Update `agents.py` and `demo.py` imports to use `agent_score_middleware`.

### Task 5: Tests And Verification

**Commands:**
- `PYTHONPATH=credit-engine:a2a-middleware:mvp-demo python3 -m unittest discover -s a2a-middleware/tests -v`
- `PYTHONPATH=credit-engine:a2a-middleware:mvp-demo python3 -m unittest discover -s mvp-demo/tests -v`
- `PYTHONPATH=credit-engine:a2a-middleware:mvp-demo python3 -m unittest discover -s credit-engine/tests -v`
- `PYTHONPATH=credit-engine:a2a-middleware:mvp-demo python3 mvp-demo/demo.py`

- [x] Middleware tests pass.
- [x] MVP demo tests still pass.
- [x] Credit engine tests still pass.
- [x] CLI demo still runs.
