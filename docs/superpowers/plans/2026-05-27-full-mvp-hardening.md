# Full MVP Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the local MVP into a production-shaped protocol demo with JWS signatures, HTTP A2A flow, and IPR anchoring.

**Architecture:** Keep existing HMAC paths for backward-compatible tests, add ES256K/JWS as the preferred CreditVC proof, extend middleware verification to accept issuer public keys, add an IPR anchor abstraction, and add a single-process HTTP demo using FastAPI TestClient to simulate client/provider calls.

**Tech Stack:** Python 3.9+, cryptography secp256k1, FastAPI TestClient, existing credit-engine and a2a-middleware.

---

### Task 1: JWS CreditVC

- [x] Add ES256K JWS signing and verification helpers in `credit-engine/agent_score_engine/jws.py`.
- [x] Add `sign_credit_vc_jws()` and `verify_credit_vc_jws()` in `credit-engine/agent_score_engine/vc.py`.
- [x] Keep HMAC proof compatibility.

### Task 2: Middleware Verification

- [x] Extend `verify_agent_card_credit()` to accept `public_key_by_issuer`.
- [x] Prefer JWS verification when proof type is `AgentScoreJWS2026`.
- [x] Preserve existing HMAC verification.

### Task 3: IPR Anchor

- [x] Add `a2a-middleware/agent_score_middleware/anchors.py`.
- [x] Add `InMemoryIPRAnchor.submit()` returning an anchor receipt.
- [x] Let FastAPI adapter optionally anchor IPR after task completion.

### Task 4: HTTP Demo

- [x] Add `http-demo/demo.py` to simulate client/provider over FastAPI TestClient.
- [x] Use JWS CreditVC for both caller and provider.
- [x] Print provider card, HTTP status, result, IPR hash, and anchor receipt.

### Task 5: Tests

- [x] Add JWS VC tests.
- [x] Add middleware JWS handshake tests.
- [x] Add anchor/HTTP adapter tests.
- [x] Run all Python tests and demo commands.
