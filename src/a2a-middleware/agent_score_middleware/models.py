from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set

from .ipr import sha256_json


TIER_RANK = {"D": 0, "C": 1, "B": 2, "A": 3, "S": 4}


@dataclass(frozen=True)
class AgentPolicy:
    min_credit_score: int = 600
    min_tier: str = "B"
    max_violation_90d: int = 2
    trusted_issuers: Set[str] = field(default_factory=set)
    require_device_binding: bool = False
    min_binding_level: str = "registration"
    trusted_device_authorities: Set[str] = field(default_factory=set)
    allowed_countries: Set[str] = field(default_factory=set)
    blocked_asns: Set[int] = field(default_factory=set)
    require_principal_co_sign_on_drift: bool = True

    def __post_init__(self) -> None:
        if self.min_tier not in TIER_RANK:
            raise ValueError("min_tier must be one of S/A/B/C/D")


@dataclass(frozen=True)
class AgentCard:
    name: str
    version: str
    endpoint: str
    skills: List[str]
    did: str
    principal: str
    credit_vc: Dict[str, Any]
    device_binding_vc: Optional[Dict[str, Any]] = None
    network_fingerprint: Optional[Dict[str, Any]] = None

    def to_a2a_dict(self) -> Dict[str, Any]:
        ext: Dict[str, Any] = {
            "did": self.did,
            "principal": self.principal,
            "credit_vc": self.credit_vc,
            "credit_authority": self.credit_vc.get("issuer"),
        }
        if self.device_binding_vc is not None:
            ext["device_binding_vc"] = self.device_binding_vc
        if self.network_fingerprint is not None:
            ext["network_fingerprint"] = self.network_fingerprint
        return {
            "name": self.name,
            "version": self.version,
            "endpoints": {"a2a": self.endpoint},
            "skills": list(self.skills),
            "x-agent-score": ext,
        }

    @classmethod
    def from_a2a_dict(cls, data: Dict[str, Any]) -> "AgentCard":
        ext = data.get("x-agent-score", {})
        return cls(
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            endpoint=data.get("endpoints", {}).get("a2a", ""),
            skills=data.get("skills", []),
            did=ext.get("did", ""),
            principal=ext.get("principal", ""),
            credit_vc=ext.get("credit_vc", {}),
            device_binding_vc=ext.get("device_binding_vc"),
            network_fingerprint=ext.get("network_fingerprint"),
        )


@dataclass(frozen=True)
class HandshakeResult:
    accepted: bool
    reason: str
    agent_did: str
    score: Optional[int] = None
    tier: Optional[str] = None
    provider_score: Optional[int] = None
    provider_tier: Optional[str] = None


@dataclass(frozen=True)
class InteractionProofRecordEnvelope:
    caller_did: str
    callee_did: str
    task_id: str
    success: bool
    on_time: bool
    result_hash: str
    caller_signature: str
    callee_signature: str

    @property
    def ipr_hash(self) -> str:
        payload = asdict(self)
        payload.pop("caller_signature")
        payload.pop("callee_signature")
        return sha256_json(payload)
