from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from typing import Any

from .models import CreditResult
from .jws import sign_json_jws, verify_json_jws


VC_CONTEXT = ("https://www.w3.org/ns/credentials/v2", "https://agent-score.org/v1")
VC_TYPES = ("VerifiableCredential", "AgentCreditCredential")
DEFAULT_VALIDITY_DAYS = 30


def build_credit_vc(
    result: CreditResult,
    issuer: str,
    issued_at: datetime | None = None,
    validity_days: int = DEFAULT_VALIDITY_DAYS,
    snapshot_root: str | None = None,
    violation_count_90d: int = 0,
    credential_status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not issuer:
        raise ValueError("issuer is required")
    if validity_days <= 0:
        raise ValueError("validity_days must be > 0")
    if violation_count_90d < 0:
        raise ValueError("violation_count_90d must be >= 0")

    issued_at = _ensure_utc(issued_at or datetime.now(timezone.utc))
    expires_at = issued_at + timedelta(days=validity_days)

    vc = {
        "@context": list(VC_CONTEXT),
        "type": list(VC_TYPES),
        "issuer": issuer,
        "validFrom": _isoformat_z(issued_at),
        "validUntil": _isoformat_z(expires_at),
        "credentialSubject": {
            "id": result.agent_id,
            "score": result.score,
            "tier": result.tier,
            "dimensions": asdict(result.dimensions),
            "violation_penalty": result.violation_penalty,
            "violation_count_90d": violation_count_90d,
            "snapshot_root": snapshot_root,
            "reason_codes": list(result.reason_codes),
        },
    }
    if credential_status is not None:
        vc["credentialStatus"] = credential_status
    return vc


def sign_credit_vc(
    vc_payload: dict[str, Any],
    issuer: str,
    secret: str,
    proof_created: datetime | None = None,
) -> dict[str, Any]:
    if not secret:
        raise ValueError("secret is required")
    if vc_payload.get("issuer") != issuer:
        raise ValueError("issuer does not match vc payload")

    proof_created = _ensure_utc(proof_created or datetime.now(timezone.utc))
    unsigned_payload = _without_proof(vc_payload)
    signature = _sign(unsigned_payload, secret)
    signed = dict(unsigned_payload)
    signed["proof"] = {
        "type": "AgentScoreHMAC2026",
        "created": _isoformat_z(proof_created),
        "verificationMethod": issuer,
        "proofPurpose": "assertionMethod",
        "jws": signature,
    }
    return signed


def verify_credit_vc(
    signed_vc: dict[str, Any],
    trusted_issuers: set[str],
    secret_by_issuer: dict[str, str],
    now: datetime | None = None,
    revoked_status_ids: set[str] | None = None,
) -> bool:
    issuer = signed_vc.get("issuer")
    if not isinstance(issuer, str) or issuer not in trusted_issuers:
        return False
    proof = signed_vc.get("proof")
    if not isinstance(proof, dict) or not isinstance(proof.get("jws"), str):
        return False
    secret = secret_by_issuer.get(issuer)
    if not secret:
        return False

    valid_from = _parse_datetime(signed_vc.get("validFrom"))
    valid_until = _parse_datetime(signed_vc.get("validUntil"))
    current = _ensure_utc(now or datetime.now(timezone.utc))
    if valid_from is None or valid_until is None or current < valid_from or current >= valid_until:
        return False
    if _is_revoked(signed_vc, revoked_status_ids):
        return False

    expected = _sign(_without_proof(signed_vc), secret)
    return hmac.compare_digest(expected, proof["jws"])


def sign_credit_vc_jws(
    vc_payload: dict[str, Any],
    issuer: str,
    private_key_pem: str,
    proof_created: datetime | None = None,
) -> dict[str, Any]:
    if vc_payload.get("issuer") != issuer:
        raise ValueError("issuer does not match vc payload")

    proof_created = _ensure_utc(proof_created or datetime.now(timezone.utc))
    created = _isoformat_z(proof_created)
    unsigned_payload = _without_proof(vc_payload)
    jws = sign_json_jws(unsigned_payload, private_key_pem, kid=issuer)
    signed = dict(unsigned_payload)
    signed["proof"] = {
        "type": "AgentScoreJWS2026",
        "created": created,
        "verificationMethod": issuer,
        "proofPurpose": "assertionMethod",
        "jws": jws,
    }
    return signed


def verify_credit_vc_jws(
    signed_vc: dict[str, Any],
    trusted_issuers: set[str],
    public_key_by_issuer: dict[str, str],
    now: datetime | None = None,
    revoked_status_ids: set[str] | None = None,
) -> bool:
    issuer = signed_vc.get("issuer")
    if not isinstance(issuer, str) or issuer not in trusted_issuers:
        return False
    proof = signed_vc.get("proof")
    if not isinstance(proof, dict) or proof.get("type") != "AgentScoreJWS2026":
        return False
    jws = proof.get("jws")
    if not isinstance(jws, str):
        return False
    public_key_pem = public_key_by_issuer.get(issuer)
    if not public_key_pem:
        return False

    valid_from = _parse_datetime(signed_vc.get("validFrom") or signed_vc.get("issuanceDate"))
    valid_until = _parse_datetime(signed_vc.get("validUntil") or signed_vc.get("expirationDate"))
    current = _ensure_utc(now or datetime.now(timezone.utc))
    if valid_from is None or valid_until is None or current < valid_from or current >= valid_until:
        return False
    if _is_revoked(signed_vc, revoked_status_ids):
        return False

    payload = verify_json_jws(jws, public_key_pem, expected_alg="ES256K", expected_kid=issuer)
    return payload == _without_proof(signed_vc)


def _sign(payload: dict[str, Any], secret: str) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hmac.new(secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def _without_proof(payload: dict[str, Any]) -> dict[str, Any]:
    copy = dict(payload)
    copy.pop("proof", None)
    return copy


def _is_revoked(signed_vc: dict[str, Any], revoked_status_ids: set[str] | None) -> bool:
    credential_status = signed_vc.get("credentialStatus")
    if not isinstance(credential_status, dict):
        return False
    status_id = credential_status.get("id")
    if not isinstance(status_id, str):
        return False
    return status_id in (revoked_status_ids or set())


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _isoformat_z(value: datetime) -> str:
    return _ensure_utc(value).isoformat(timespec="seconds").replace("+00:00", "Z")


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None
