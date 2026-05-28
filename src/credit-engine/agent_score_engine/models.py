from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional


ValidationType = Literal["tee", "re_execution", "zkml"]
Tier = Literal["S", "A", "B", "C", "D"]
BindingLevel = Literal["none", "registration", "runtime", "strong"]


@dataclass(frozen=True)
class InteractionProofRecord:
    client_id: str
    success: bool
    on_time: bool
    caller_signed: bool = True
    callee_signed: bool = True

    @property
    def dual_signed(self) -> bool:
        return self.caller_signed and self.callee_signed


@dataclass(frozen=True)
class StakeSnapshot:
    asset: str
    usd_value: float
    weight: float = 1.0
    lock_days_remaining: int = 30


@dataclass(frozen=True)
class ViolationEvent:
    severity: int
    days_ago: int

    def __post_init__(self) -> None:
        if not 0 <= self.severity <= 100:
            raise ValueError("severity must be in [0, 100]")
        if self.days_ago < 0:
            raise ValueError("days_ago must be >= 0")


@dataclass(frozen=True)
class EndorsementEdge:
    endorser_id: str
    score: float
    cluster_id: str


@dataclass(frozen=True)
class ValidationAttestation:
    validator_id: str
    validation_type: ValidationType
    passed: bool = True


@dataclass(frozen=True)
class DeviceAttestation:
    attestation_type: str
    device_pubkey_hash: str
    agent_did: str
    timestamp: int
    quote: Optional[str] = None
    signature: Optional[str] = None
    nonce: Optional[str] = None


@dataclass(frozen=True)
class NetworkFingerprint:
    country_code: Optional[str] = None
    asn: Optional[int] = None
    ipv4_prefix: Optional[str] = None
    ipv6_prefix: Optional[str] = None
    is_vpn: Optional[bool] = None
    is_tor_exit: Optional[bool] = None
    observer_did: Optional[str] = None
    timestamp: Optional[int] = None


@dataclass(frozen=True)
class DeviceProfile:
    binding_level: BindingLevel = "none"
    attestation: Optional[DeviceAttestation] = None
    network: Optional[NetworkFingerprint] = None
    registered_country_code: Optional[str] = None
    registered_asn: Optional[int] = None
    has_network_drift: bool = False
    has_principal_co_sign: bool = False


@dataclass(frozen=True)
class PrincipalProfile:
    score: float = 500.0
    flagged: bool = False
    vc_expired: bool = False


@dataclass(frozen=True)
class CreditInput:
    agent_id: str
    interactions: list[InteractionProofRecord] = field(default_factory=list)
    stakes: list[StakeSnapshot] = field(default_factory=list)
    violations: list[ViolationEvent] = field(default_factory=list)
    endorsements: list[EndorsementEdge] = field(default_factory=list)
    validations: list[ValidationAttestation] = field(default_factory=list)
    principal: PrincipalProfile = field(default_factory=PrincipalProfile)
    device: DeviceProfile = field(default_factory=DeviceProfile)


@dataclass(frozen=True)
class DimensionScores:
    behavior: float
    stake: float
    endorsement: float
    validation: float
    device: float
    principal: float


@dataclass(frozen=True)
class CreditResult:
    agent_id: str
    score: int
    tier: Tier
    dimensions: DimensionScores
    violation_penalty: float
    reason_codes: tuple[str, ...]
