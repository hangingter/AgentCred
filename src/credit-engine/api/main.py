from __future__ import annotations

import os
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator as pydantic_validator

from agent_score_engine import (
    VALIDATION_TYPE_WEIGHTS,
    CreditInput,
    DeviceAttestation,
    DeviceProfile,
    EndorsementEdge,
    InteractionProofRecord,
    NetworkFingerprint,
    PrincipalProfile,
    StakeSnapshot,
    ValidationAttestation,
    ViolationEvent,
    build_credit_vc,
    calculate_credit_score,
    export_json_schemas,
    sign_credit_vc,
)


DEFAULT_ISSUER = "did:ethr:0x2105:0x000000000000000000000000000000000000CAFE"
DEFAULT_SECRET_ENV = "AGENT_SCORE_AUTHORITY_SECRET"

app = FastAPI(title="Agent-Score Credit Engine", version="0.1.0")


class InteractionProofRecordRequest(BaseModel):
    client_id: str
    success: bool
    on_time: bool
    caller_signed: bool = True
    callee_signed: bool = True


class StakeSnapshotRequest(BaseModel):
    asset: str
    usd_value: float = Field(ge=0)
    weight: float = Field(default=1.0, ge=0)
    lock_days_remaining: int = Field(default=30, ge=0)


class ViolationEventRequest(BaseModel):
    severity: int = Field(ge=0, le=100)
    days_ago: int = Field(ge=0)


class EndorsementEdgeRequest(BaseModel):
    endorser_id: str
    score: float = Field(ge=0, le=100)
    cluster_id: str


ALLOWED_VALIDATION_TYPES = set(VALIDATION_TYPE_WEIGHTS.keys())


class ValidationAttestationRequest(BaseModel):
    validator_id: str
    validation_type: str
    passed: bool = True

    @pydantic_validator("validation_type")
    @classmethod
    def _validate_type(cls, v: str) -> str:
        if v not in ALLOWED_VALIDATION_TYPES:
            raise ValueError(f"validation_type must be one of {sorted(ALLOWED_VALIDATION_TYPES)}")
        return v


class PrincipalProfileRequest(BaseModel):
    score: float = Field(default=500.0, ge=0, le=1000)
    flagged: bool = False
    vc_expired: bool = False


class DeviceAttestationRequest(BaseModel):
    attestation_type: str
    device_pubkey_hash: str
    agent_did: str
    timestamp: int
    quote: Optional[str] = None
    signature: Optional[str] = None
    nonce: Optional[str] = None


class NetworkFingerprintRequest(BaseModel):
    country_code: Optional[str] = None
    asn: Optional[int] = None
    ipv4_prefix: Optional[str] = None
    ipv6_prefix: Optional[str] = None
    is_vpn: Optional[bool] = None
    is_tor_exit: Optional[bool] = None
    observer_did: Optional[str] = None
    timestamp: Optional[int] = None


class DeviceProfileRequest(BaseModel):
    binding_level: str = "none"
    attestation: Optional[DeviceAttestationRequest] = None
    network: Optional[NetworkFingerprintRequest] = None
    registered_country_code: Optional[str] = None
    registered_asn: Optional[int] = None
    has_network_drift: bool = False
    has_principal_co_sign: bool = False

    @pydantic_validator("binding_level")
    @classmethod
    def _validate_binding_level(cls, v: str) -> str:
        allowed = {"none", "registration", "runtime", "strong"}
        if v not in allowed:
            raise ValueError(f"binding_level must be one of {sorted(allowed)}")
        return v


class CreditInputRequest(BaseModel):
    agent_id: str
    interactions: list[InteractionProofRecordRequest] = Field(default_factory=list)
    stakes: list[StakeSnapshotRequest] = Field(default_factory=list)
    violations: list[ViolationEventRequest] = Field(default_factory=list)
    endorsements: list[EndorsementEdgeRequest] = Field(default_factory=list)
    validations: list[ValidationAttestationRequest] = Field(default_factory=list)
    principal: PrincipalProfileRequest = Field(default_factory=PrincipalProfileRequest)
    device: DeviceProfileRequest = Field(default_factory=DeviceProfileRequest)


class IssueVCRequest(BaseModel):
    credit_input: CreditInputRequest
    issuer: str = DEFAULT_ISSUER
    snapshot_root: Optional[str] = None
    violation_count_90d: int = Field(default=0, ge=0)
    issued_at: Optional[datetime] = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/schemas")
def schemas() -> dict[str, dict[str, Any]]:
    return export_json_schemas()


@app.post("/score")
def score(request: CreditInputRequest) -> dict[str, Any]:
    result = calculate_credit_score(_to_credit_input(request))
    return _credit_result_to_dict(result)


@app.post("/issue-vc")
def issue_vc(request: IssueVCRequest) -> dict[str, Any]:
    secret = os.getenv(DEFAULT_SECRET_ENV)
    if not secret:
        raise HTTPException(
            status_code=500,
            detail=f"{DEFAULT_SECRET_ENV} must be set before issuing CreditVC",
        )

    result = calculate_credit_score(_to_credit_input(request.credit_input))
    payload = build_credit_vc(
        result,
        issuer=request.issuer,
        issued_at=request.issued_at,
        snapshot_root=request.snapshot_root,
        violation_count_90d=request.violation_count_90d,
    )
    return sign_credit_vc(
        payload,
        issuer=request.issuer,
        secret=secret,
        proof_created=datetime.now(timezone.utc),
    )


def _to_credit_input(request: CreditInputRequest) -> CreditInput:
    return CreditInput(
        agent_id=request.agent_id,
        interactions=[
            InteractionProofRecord(
                client_id=item.client_id,
                success=item.success,
                on_time=item.on_time,
                caller_signed=item.caller_signed,
                callee_signed=item.callee_signed,
            )
            for item in request.interactions
        ],
        stakes=[
            StakeSnapshot(
                asset=item.asset,
                usd_value=item.usd_value,
                weight=item.weight,
                lock_days_remaining=item.lock_days_remaining,
            )
            for item in request.stakes
        ],
        violations=[
            ViolationEvent(severity=item.severity, days_ago=item.days_ago)
            for item in request.violations
        ],
        endorsements=[
            EndorsementEdge(
                endorser_id=item.endorser_id,
                score=item.score,
                cluster_id=item.cluster_id,
            )
            for item in request.endorsements
        ],
        validations=[
            ValidationAttestation(
                validator_id=item.validator_id,
                validation_type=item.validation_type,  # type: ignore[arg-type]
                passed=item.passed,
            )
            for item in request.validations
        ],
        principal=PrincipalProfile(
            score=request.principal.score,
            flagged=request.principal.flagged,
            vc_expired=request.principal.vc_expired,
        ),
        device=DeviceProfile(
            binding_level=request.device.binding_level,  # type: ignore[arg-type]
            attestation=(
                DeviceAttestation(**request.device.attestation.dict())
                if request.device.attestation is not None
                else None
            ),
            network=(
                NetworkFingerprint(**request.device.network.dict())
                if request.device.network is not None
                else None
            ),
            registered_country_code=request.device.registered_country_code,
            registered_asn=request.device.registered_asn,
            has_network_drift=request.device.has_network_drift,
            has_principal_co_sign=request.device.has_principal_co_sign,
        ),
    )


def _credit_result_to_dict(result: Any) -> dict[str, Any]:
    return asdict(result)
