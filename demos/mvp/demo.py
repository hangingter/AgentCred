from __future__ import annotations

import json
from typing import Any, Dict

from agent_score_engine import (
    CreditInput,
    EndorsementEdge,
    InteractionProofRecord,
    PrincipalProfile,
    StakeSnapshot,
    ValidationAttestation,
)

from agents import LocalAgent
from agent_score_middleware import AgentPolicy, verify_agent_card_credit


AUTHORITY_ISSUER = "did:ethr:0x2105:0x000000000000000000000000000000000000CAFE"
AUTHORITY_SECRET = "local-demo-authority-secret"


def run_demo(print_output: bool = True) -> Dict[str, Any]:
    client = _build_client_agent()
    provider = _build_provider_agent()
    policy = AgentPolicy(
        min_credit_score=600,
        min_tier="B",
        max_violation_90d=2,
        trusted_issuers={AUTHORITY_ISSUER},
    )

    initial_score = provider.current_score()
    provider_card = provider.agent_card()
    handshake = verify_agent_card_credit(
        provider_card,
        policy,
        secret_by_issuer={AUTHORITY_ISSUER: AUTHORITY_SECRET},
    )

    if not handshake.accepted:
        raise RuntimeError(f"Handshake rejected: {handshake.reason}")

    task = {
        "task_id": "task-618-risk-check",
        "prompt": "Evaluate whether this provider can handle a finance-grade A2A task.",
    }
    task_result = provider.handle_task(task)
    ipr = provider.build_ipr(client, task, task_result)
    provider.append_ipr_sample(ipr)
    refreshed_score = provider.current_score()

    summary = {
        "agent_card": provider_card.to_a2a_dict(),
        "handshake": {
            "accepted": handshake.accepted,
            "reason": handshake.reason,
            "provider_score": handshake.provider_score,
            "provider_tier": handshake.provider_tier,
        },
        "task_result": task_result,
        "ipr": {
            "hash": ipr.ipr_hash,
            "caller_signature": ipr.caller_signature,
            "callee_signature": ipr.callee_signature,
        },
        "score_delta": {
            "before": initial_score.score,
            "after": refreshed_score.score,
            "before_tier": initial_score.tier,
            "after_tier": refreshed_score.tier,
            "after_reason_codes": list(refreshed_score.reason_codes),
        },
    }

    if print_output:
        _print_summary(summary)
    return summary


def _build_client_agent() -> LocalAgent:
    return LocalAgent(
        name="client-agent",
        did="did:ethr:0x2105:0x0000000000000000000000000000000000000001",
        principal="did:web:client.example",
        endpoint="local://client-agent/a2a",
        skills=["task.request"],
        initial_credit_input=CreditInput(
            agent_id="client",
            interactions=[
                InteractionProofRecord(client_id=f"client-peer-{index % 3}", success=True, on_time=True)
                for index in range(12)
            ],
            stakes=[StakeSnapshot(asset="USDC", usd_value=2_500)],
            validations=[ValidationAttestation(validator_id="tee-lab", validation_type="tee")],
            principal=PrincipalProfile(score=780),
        ),
        authority_issuer=AUTHORITY_ISSUER,
        authority_secret=AUTHORITY_SECRET,
        agent_secret="client-agent-secret",
    )


def _build_provider_agent() -> LocalAgent:
    return LocalAgent(
        name="risk-check-provider",
        did="did:ethr:0x2105:0x0000000000000000000000000000000000008004",
        principal="did:web:provider.example",
        endpoint="local://risk-check-provider/a2a",
        skills=["finance.read", "risk-check"],
        initial_credit_input=CreditInput(
            agent_id="provider",
            interactions=[
                InteractionProofRecord(client_id=f"buyer-{index % 5}", success=True, on_time=True)
                for index in range(14)
            ],
            stakes=[
                StakeSnapshot(asset="USDC", usd_value=4_000, weight=1.0, lock_days_remaining=90),
                StakeSnapshot(asset="ETH", usd_value=2_000, weight=0.9, lock_days_remaining=60),
            ],
            endorsements=[
                EndorsementEdge(endorser_id="bank-agent", score=86, cluster_id="finance"),
                EndorsementEdge(endorser_id="audit-agent", score=82, cluster_id="audit"),
            ],
            validations=[
                ValidationAttestation(validator_id="tee-lab", validation_type="tee"),
                ValidationAttestation(validator_id="reexec-lab", validation_type="re_execution"),
            ],
            principal=PrincipalProfile(score=820),
        ),
        authority_issuer=AUTHORITY_ISSUER,
        authority_secret=AUTHORITY_SECRET,
        agent_secret="provider-agent-secret",
    )


def _print_summary(summary: Dict[str, Any]) -> None:
    print("\n=== Agent-Score MVP Demo ===")
    print("\n[1] Provider Agent Card")
    print(json.dumps(summary["agent_card"], indent=2, ensure_ascii=False))
    print("\n[2] A2A Trust Handshake")
    print(json.dumps(summary["handshake"], indent=2, ensure_ascii=False))
    print("\n[3] A2A Task Result")
    print(json.dumps(summary["task_result"], indent=2, ensure_ascii=False))
    print("\n[4] Dual-Signed IPR")
    print(json.dumps(summary["ipr"], indent=2, ensure_ascii=False))
    print("\n[5] Score Refresh")
    print(json.dumps(summary["score_delta"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run_demo()
