from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastapi.testclient import TestClient

from agent_score_engine import (
    CreditInput,
    InteractionProofRecord,
    PrincipalProfile,
    StakeSnapshot,
    ValidationAttestation,
    build_credit_vc,
    calculate_credit_score,
    generate_es256k_private_key_pem,
    public_key_pem_from_private_key,
    sign_credit_vc_jws,
)
from agent_score_middleware import AgentCard, AgentPolicy, InMemoryIPRAnchor, create_agent_app


AUTHORITY_DID = "did:ethr:0x2105:0x000000000000000000000000000000000000CAFE"


def run_http_demo(print_output: bool = True) -> Dict[str, Any]:
    authority_private_key = generate_es256k_private_key_pem()
    authority_public_key = public_key_pem_from_private_key(authority_private_key)
    caller_card = _build_card("caller-agent", authority_private_key)
    provider_card = _build_card("provider-agent", authority_private_key)
    anchor = InMemoryIPRAnchor()
    app = create_agent_app(
        provider_card=provider_card,
        provider_secret="provider-http-secret",
        policy=AgentPolicy(min_credit_score=600, min_tier="B", trusted_issuers={AUTHORITY_DID}),
        secret_by_issuer={},
        public_key_by_issuer={AUTHORITY_DID: authority_public_key},
        ipr_anchor=anchor,
        task_handler=lambda task: {
            "task_id": task["task_id"],
            "status": "completed",
            "answer": f"HTTP provider handled: {task.get('prompt', '')}",
        },
    )
    client = TestClient(app)

    provider_card_response = client.get("/agent-card")
    a2a_response = client.post(
        "/a2a",
        json={
            "caller_card": _http_card_payload(caller_card.to_a2a_dict()),
            "task": {"task_id": "http-task-1", "prompt": "run production-shaped A2A trust check"},
            "caller_signature": "http-demo-caller-signature",
        },
    )

    summary = {
        "provider_card_status": provider_card_response.status_code,
        "provider_card": provider_card_response.json(),
        "a2a_status": a2a_response.status_code,
        "a2a_response": a2a_response.json(),
        "anchor_count": len(anchor.receipts),
    }
    if print_output:
        _print_summary(summary)
    return summary


def _build_card(name: str, authority_private_key: str) -> AgentCard:
    did = f"did:ethr:0x2105:0x{name.replace('-', '')}"
    credit_input = CreditInput(
        agent_id=did,
        interactions=[
            InteractionProofRecord(client_id=f"peer-{index % 4}", success=True, on_time=True)
            for index in range(16)
        ],
        stakes=[StakeSnapshot(asset="USDC", usd_value=3_000, lock_days_remaining=90)],
        validations=[ValidationAttestation(validator_id="tee-lab", validation_type="tee")],
        principal=PrincipalProfile(score=820),
    )
    result = calculate_credit_score(credit_input)
    issued_at = datetime.now(timezone.utc) - timedelta(days=1)
    payload = build_credit_vc(result, issuer=AUTHORITY_DID, issued_at=issued_at)
    signed = sign_credit_vc_jws(payload, issuer=AUTHORITY_DID, private_key_pem=authority_private_key)
    return AgentCard(
        name=name,
        version="0.1.0",
        endpoint=f"http://testserver/{name}/a2a",
        skills=["risk-check"],
        did=did,
        principal=f"did:web:{name}.example",
        credit_vc=signed,
    )


def _http_card_payload(card_dict: Dict[str, Any]) -> Dict[str, Any]:
    extension = card_dict["x-agent-score"]
    return {
        "name": card_dict["name"],
        "version": card_dict["version"],
        "endpoint": card_dict["endpoints"]["a2a"],
        "skills": card_dict["skills"],
        "did": extension["did"],
        "principal": extension["principal"],
        "credit_vc": extension["credit_vc"],
    }


def _print_summary(summary: Dict[str, Any]) -> None:
    print("\n=== Agent-Score HTTP A2A Demo ===")
    print("\n[1] Provider Agent Card")
    print(json.dumps(summary["provider_card"], indent=2, ensure_ascii=False))
    print("\n[2] HTTP A2A Response")
    print(json.dumps(summary["a2a_response"], indent=2, ensure_ascii=False))
    print("\n[3] Anchor Count")
    print(summary["anchor_count"])


if __name__ == "__main__":
    run_http_demo()
