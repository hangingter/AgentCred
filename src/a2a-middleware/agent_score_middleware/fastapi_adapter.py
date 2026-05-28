from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .handshake import verify_agent_card_credit
from .ipr import sha256_json, sign_payload
from .models import AgentCard, AgentPolicy, InteractionProofRecordEnvelope


TaskHandler = Callable[[Dict[str, Any]], Dict[str, Any]]


class AgentCardRequest(BaseModel):
    name: str
    version: str
    endpoint: str
    skills: list[str]
    did: str
    principal: str
    credit_vc: Dict[str, Any]
    device_binding_vc: Optional[Dict[str, Any]] = None
    network_fingerprint: Optional[Dict[str, Any]] = None

    def to_agent_card(self) -> AgentCard:
        return AgentCard(
            name=self.name,
            version=self.version,
            endpoint=self.endpoint,
            skills=self.skills,
            did=self.did,
            principal=self.principal,
            credit_vc=self.credit_vc,
            device_binding_vc=self.device_binding_vc,
            network_fingerprint=self.network_fingerprint,
        )


class A2ARequest(BaseModel):
    caller_card: AgentCardRequest
    task: Dict[str, Any]
    caller_signature: Optional[str] = None


def create_agent_app(
    provider_card: AgentCard,
    provider_secret: str,
    policy: AgentPolicy,
    secret_by_issuer: Dict[str, str],
    task_handler: TaskHandler,
    public_key_by_issuer: Optional[Dict[str, str]] = None,
    public_key_by_device_authority: Optional[Dict[str, str]] = None,
    ipr_anchor: Any = None,
) -> FastAPI:
    app = FastAPI(title=f"{provider_card.name} Agent-Score Adapter", version=provider_card.version)

    @app.get("/agent-card")
    def get_agent_card() -> Dict[str, Any]:
        return provider_card.to_a2a_dict()

    @app.post("/a2a")
    def a2a(request: A2ARequest) -> Dict[str, Any]:
        caller_card = request.caller_card.to_agent_card()
        handshake = verify_agent_card_credit(
            caller_card,
            policy,
            secret_by_issuer=secret_by_issuer or {},
            public_key_by_issuer=public_key_by_issuer or {},
            public_key_by_device_authority=public_key_by_device_authority or {},
        )
        if not handshake.accepted:
            raise HTTPException(status_code=403, detail={"reason": handshake.reason})

        result = task_handler(request.task)
        result_hash = sha256_json(result)
        unsigned_ipr = {
            "caller_did": caller_card.did,
            "callee_did": provider_card.did,
            "task_id": request.task["task_id"],
            "success": result.get("status") == "completed",
            "on_time": True,
            "result_hash": result_hash,
        }
        if request.caller_signature is None:
            raise HTTPException(
                status_code=400,
                detail={"reason": "MISSING_CALLER_SIGNATURE"},
            )
        ipr = InteractionProofRecordEnvelope(
            **unsigned_ipr,
            caller_signature=request.caller_signature,
            callee_signature=sign_payload(unsigned_ipr, provider_secret),
        )

        response = {
            "handshake": {
                "accepted": handshake.accepted,
                "reason": handshake.reason,
                "provider_score": handshake.provider_score,
                "provider_tier": handshake.provider_tier,
            },
            "result": result,
            "ipr": {
                "hash": ipr.ipr_hash,
                "caller_signature": ipr.caller_signature,
                "callee_signature": ipr.callee_signature,
            },
        }
        if ipr_anchor is not None:
            response["anchor"] = ipr_anchor.submit(ipr)
        return response

    return app
