from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Any, Dict, List

from agent_score_engine import (
    CreditInput,
    InteractionProofRecord,
    build_credit_vc,
    calculate_credit_score,
    sign_credit_vc,
)
from agent_score_middleware import AgentCard, InteractionProofRecordEnvelope, sign_payload, sha256_json


class LocalAgent:
    def __init__(
        self,
        name: str,
        did: str,
        principal: str,
        endpoint: str,
        skills: List[str],
        initial_credit_input: CreditInput,
        authority_issuer: str,
        authority_secret: str,
        agent_secret: str,
    ) -> None:
        self.name = name
        self.did = did
        self.principal = principal
        self.endpoint = endpoint
        self.skills = skills
        self.credit_input = replace(initial_credit_input, agent_id=did)
        self.authority_issuer = authority_issuer
        self.authority_secret = authority_secret
        self.agent_secret = agent_secret

    def current_score(self):
        return calculate_credit_score(self.credit_input)

    def agent_card(self) -> AgentCard:
        result = self.current_score()
        vc_payload = build_credit_vc(
            result,
            issuer=self.authority_issuer,
            issued_at=datetime.now(timezone.utc),
            snapshot_root=sha256_json({"agent": self.did, "score": result.score}),
            violation_count_90d=sum(1 for item in self.credit_input.violations if item.days_ago <= 90),
        )
        signed_vc = sign_credit_vc(
            vc_payload,
            issuer=self.authority_issuer,
            secret=self.authority_secret,
            proof_created=datetime.now(timezone.utc),
        )
        return AgentCard(
            name=self.name,
            version="0.1.0",
            endpoint=self.endpoint,
            skills=list(self.skills),
            did=self.did,
            principal=self.principal,
            credit_vc=signed_vc,
        )

    def handle_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = task.get("prompt", "")
        return {
            "task_id": task["task_id"],
            "provider": self.did,
            "status": "completed",
            "answer": f"{self.name} accepted task '{prompt}' and produced a verified result.",
        }

    def build_ipr(
        self,
        caller: "LocalAgent",
        task: Dict[str, Any],
        result: Dict[str, Any],
        success: bool = True,
        on_time: bool = True,
    ) -> InteractionProofRecordEnvelope:
        result_hash = sha256_json(result)
        unsigned = {
            "caller_did": caller.did,
            "callee_did": self.did,
            "task_id": task["task_id"],
            "success": success,
            "on_time": on_time,
            "result_hash": result_hash,
        }
        return InteractionProofRecordEnvelope(
            caller_did=caller.did,
            callee_did=self.did,
            task_id=task["task_id"],
            success=success,
            on_time=on_time,
            result_hash=result_hash,
            caller_signature=sign_payload(unsigned, caller.agent_secret),
            callee_signature=sign_payload(unsigned, self.agent_secret),
        )

    def append_ipr_sample(self, ipr: InteractionProofRecordEnvelope) -> None:
        if ipr.callee_did != self.did:
            raise ValueError("IPR callee does not match agent DID")
        self.credit_input.interactions.append(
            InteractionProofRecord(
                client_id=ipr.caller_did,
                success=ipr.success,
                on_time=ipr.on_time,
                caller_signed=bool(ipr.caller_signature),
                callee_signed=bool(ipr.callee_signature),
            )
        )
