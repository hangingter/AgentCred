from .anchors import AnchorReceipt, InMemoryIPRAnchor
from .handshake import verify_agent_card_credit
from .ipr import sha256_json, sign_payload, sign_payload_jws, verify_payload_jws
from .models import (
    AgentCard,
    AgentPolicy,
    HandshakeResult,
    InteractionProofRecordEnvelope,
    TIER_RANK,
)
from .resolvers import InMemoryCredentialStatusResolver, InMemoryTrustRegistry, StaticDIDKeyResolver

try:
    from .fastapi_adapter import create_agent_app
except ImportError:  # FastAPI is an optional adapter dependency.
    create_agent_app = None  # type: ignore[assignment]

__all__ = [
    "AgentCard",
    "AgentPolicy",
    "AnchorReceipt",
    "HandshakeResult",
    "InMemoryIPRAnchor",
    "InMemoryCredentialStatusResolver",
    "InMemoryTrustRegistry",
    "InteractionProofRecordEnvelope",
    "TIER_RANK",
    "StaticDIDKeyResolver",
    "sha256_json",
    "sign_payload",
    "sign_payload_jws",
    "verify_payload_jws",
    "verify_agent_card_credit",
    "create_agent_app",
]
