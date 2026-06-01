from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from agent_score_engine import verify_credit_vc, verify_credit_vc_jws

from .models import AgentCard, AgentPolicy, HandshakeResult, TIER_RANK
from .resolvers import CredentialStatusResolver, DIDKeyResolver, TrustRegistryReader


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _parse_datetime(value: Any) -> Optional[datetime]:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _verify_device_binding(
    card: AgentCard,
    policy: AgentPolicy,
    public_key_by_device_authority: Dict[str, str] | None,
    did_key_resolver: DIDKeyResolver | None,
    credential_status_resolver: CredentialStatusResolver | None,
    trust_registry: TrustRegistryReader | None,
    now: datetime,
) -> Optional[str]:
    if not policy.require_device_binding:
        return None
    device_vc = card.device_binding_vc
    if not device_vc:
        return "MISSING_DEVICE_BINDING"
    issuer = device_vc.get("issuer")
    if policy.trusted_device_authorities and issuer not in policy.trusted_device_authorities:
        return "UNTRUSTED_DEVICE_AUTHORITY"
    if (
        isinstance(issuer, str)
        and trust_registry is not None
        and not trust_registry.is_trusted_device_authority(issuer)
    ):
        return "UNTRUSTED_DEVICE_AUTHORITY"
    valid_from = _parse_datetime(device_vc.get("validFrom") or device_vc.get("issuanceDate"))
    valid_until = _parse_datetime(device_vc.get("validUntil") or device_vc.get("expirationDate"))
    if valid_from is None or valid_until is None or now < valid_from or now >= valid_until:
        return "EXPIRED_DEVICE_BINDING"
    proof = device_vc.get("proof", {}) if isinstance(device_vc, dict) else {}
    if isinstance(proof, dict) and proof.get("type") == "AgentScoreJWS2026":
        jws = proof.get("jws")
        pubkey = (public_key_by_device_authority or {}).get(issuer) if isinstance(issuer, str) else None
        if pubkey is None and isinstance(issuer, str) and did_key_resolver is not None:
            pubkey = did_key_resolver.public_key_for(issuer)
        if not jws or not pubkey:
            return "INVALID_DEVICE_BINDING"
        revoked_status_ids = _revoked_status_ids(device_vc, credential_status_resolver)
        if revoked_status_ids is None:
            return "REVOKED_DEVICE_BINDING"
        if not verify_credit_vc_jws(
            device_vc,
            {issuer},
            {issuer: pubkey},
            now=now,
            revoked_status_ids=revoked_status_ids,
        ):
            return "INVALID_DEVICE_BINDING"
    subject = device_vc.get("credentialSubject", {}) if isinstance(device_vc, dict) else {}
    if subject.get("id") != card.did:
        return "DEVICE_BINDING_MISMATCH"
    binding_level = subject.get("binding_level", "none")
    level_rank = {"none": 4, "registration": 3, "runtime": 2, "strong": 1}
    if level_rank.get(binding_level, 99) > level_rank.get(policy.min_binding_level, 99):
        return "BINDING_LEVEL_BELOW_THRESHOLD"

    net_fp = card.network_fingerprint or {}
    country = net_fp.get("country_code") if isinstance(net_fp, dict) else None
    asn = net_fp.get("asn") if isinstance(net_fp, dict) else None
    if policy.allowed_countries and country not in policy.allowed_countries:
        return "COUNTRY_NOT_ALLOWED"
    if policy.blocked_asns and asn in policy.blocked_asns:
        return "ASN_BLOCKED"

    registered_country = subject.get("registered_country_code")
    registered_asn = subject.get("registered_asn")
    drift = False
    if registered_country and country and country != registered_country:
        drift = True
    if registered_asn is not None and asn is not None and asn != registered_asn:
        drift = True
    if drift and policy.require_principal_co_sign_on_drift:
        has_co_sign = bool(net_fp.get("principal_co_signature")) if isinstance(net_fp, dict) else False
        if not has_co_sign:
            return "NETWORK_DRIFT_WITHOUT_PRINCIPAL_COSIGN"

    return None


def verify_agent_card_credit(
    card: AgentCard,
    policy: AgentPolicy,
    secret_by_issuer: Dict[str, str] | None = None,
    public_key_by_issuer: Dict[str, str] | None = None,
    public_key_by_device_authority: Dict[str, str] | None = None,
    did_key_resolver: DIDKeyResolver | None = None,
    credential_status_resolver: CredentialStatusResolver | None = None,
    trust_registry: TrustRegistryReader | None = None,
    now: datetime | None = None,
) -> HandshakeResult:
    if card.did is None:
        return HandshakeResult(False, "MISSING_DID", card.did)
    if (
        policy.require_registered_agent
        and trust_registry is not None
        and not trust_registry.is_known_agent(card.did)
    ):
        return HandshakeResult(False, "UNREGISTERED_AGENT", card.did)
    vc = card.credit_vc
    if not vc:
        return HandshakeResult(False, "MISSING_CREDIT_VC", card.did)
    issuer = vc.get("issuer")
    if policy.trusted_issuers and issuer not in policy.trusted_issuers:
        return HandshakeResult(False, "UNTRUSTED_ISSUER", card.did)
    if (
        isinstance(issuer, str)
        and trust_registry is not None
        and not trust_registry.is_trusted_credit_authority(issuer)
    ):
        return HandshakeResult(False, "UNTRUSTED_ISSUER", card.did)

    proof = vc.get("proof", {})
    proof_type = proof.get("type") if isinstance(proof, dict) else None
    current = _ensure_utc(now or datetime.now(timezone.utc))
    revoked_status_ids = _revoked_status_ids(vc, credential_status_resolver)
    if revoked_status_ids is None:
        return HandshakeResult(False, "REVOKED_CREDENTIAL", card.did)
    if proof_type == "AgentScoreJWS2026":
        resolved_public_keys = dict(public_key_by_issuer or {})
        if isinstance(issuer, str) and issuer not in resolved_public_keys and did_key_resolver is not None:
            resolved = did_key_resolver.public_key_for(issuer)
            if resolved:
                resolved_public_keys[issuer] = resolved
        trusted_issuers = policy.trusted_issuers or ({issuer} if isinstance(issuer, str) else set())
        verified = verify_credit_vc_jws(
            vc,
            trusted_issuers,
            resolved_public_keys,
            now=current,
            revoked_status_ids=revoked_status_ids,
        )
    elif proof_type == "AgentScoreHMAC2026":
        trusted_issuers = policy.trusted_issuers or ({issuer} if isinstance(issuer, str) else set())
        verified = verify_credit_vc(
            vc,
            trusted_issuers,
            secret_by_issuer or {},
            now=current,
            revoked_status_ids=revoked_status_ids,
        )
    else:
        return HandshakeResult(False, "INVALID_CREDIT_VC", card.did)
    if not verified:
        return HandshakeResult(False, "INVALID_CREDIT_VC", card.did)

    subject = vc.get("credentialSubject", {}) if isinstance(vc, dict) else {}
    score = subject.get("credit_score", subject.get("score", 0))
    tier = subject.get("credit_tier", subject.get("tier", "D"))
    if not isinstance(score, int) or score < policy.min_credit_score:
        return HandshakeResult(False, "SCORE_BELOW_THRESHOLD", card.did)
    if not isinstance(tier, str) or TIER_RANK.get(tier, -1) < TIER_RANK.get(policy.min_tier, -1):
        return HandshakeResult(False, "TIER_BELOW_THRESHOLD", card.did)

    violations = subject.get("violations_90d", subject.get("violation_count_90d", 0))
    if isinstance(violations, int) and violations > policy.max_violation_90d:
        return HandshakeResult(False, "VIOLATION_EXCEEDED", card.did)

    device_reason = _verify_device_binding(
        card,
        policy,
        public_key_by_device_authority,
        did_key_resolver,
        credential_status_resolver,
        trust_registry,
        current,
    )
    if device_reason:
        return HandshakeResult(False, device_reason, card.did)

    return HandshakeResult(True, "ACCEPTED", card.did, score=int(score), tier=tier)


def _revoked_status_ids(
    vc: Dict[str, Any],
    credential_status_resolver: CredentialStatusResolver | None,
) -> set[str] | None:
    credential_status = vc.get("credentialStatus")
    if not isinstance(credential_status, dict):
        return set()
    status_id = credential_status.get("id")
    if not isinstance(status_id, str):
        return set()
    if credential_status_resolver is not None and credential_status_resolver.is_revoked(status_id):
        return None
    return set()
