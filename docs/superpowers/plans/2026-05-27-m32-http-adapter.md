# M3.2 HTTP Adapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a FastAPI adapter that demonstrates Agent-Score trust handshake over HTTP.

**Architecture:** Keep the core middleware web-framework agnostic, and add an optional FastAPI adapter module. The adapter exposes `GET /agent-card` and `POST /a2a`, verifies the caller `AgentCard` against an `AgentPolicy`, invokes a task handler, and returns task result plus IPR. Tests use FastAPI `TestClient`, avoiding multi-process setup.

**Tech Stack:** Python 3.9+, FastAPI, stdlib typing/dataclasses, existing `credit-engine` and `a2a-middleware`.

---

### Task 1: FastAPI Adapter

**Files:**
- Create: `a2a-middleware/agent_score_middleware/fastapi_adapter.py`
- Modify: `a2a-middleware/agent_score_middleware/__init__.py`

- [x] Add `create_agent_app()` factory.
- [x] Add `GET /agent-card`.
- [x] Add `POST /a2a` with caller card, task payload, trust handshake, task handler, IPR builder.
- [x] Return 403 when trust handshake rejects caller.

### Task 2: Adapter Tests

**Files:**
- Create: `a2a-middleware/tests/test_fastapi_adapter.py`

- [x] Test `GET /agent-card` returns A2A-compatible card.
- [x] Test valid caller can invoke `POST /a2a`.
- [x] Test untrusted issuer receives 403.
- [x] Test response contains task result and IPR hash.

### Task 3: Verification

**Commands:**
- `PYTHONPATH=credit-engine:a2a-middleware:mvp-demo python3 -m unittest discover -s a2a-middleware/tests -v`
- `PYTHONPATH=credit-engine:a2a-middleware:mvp-demo python3 -m unittest discover -s mvp-demo/tests -v`
- `PYTHONPATH=credit-engine:a2a-middleware:mvp-demo python3 -m unittest discover -s credit-engine/tests -v`

- [x] All tests pass.

### Task 4: Spec Update

**Files:**
- Modify: `protocol/SPEC.md`

- [x] Add section for FastAPI adapter endpoints and request/response shape.
