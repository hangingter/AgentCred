from __future__ import annotations

import math
from collections import Counter, defaultdict

from .models import (
    CreditInput,
    CreditResult,
    DimensionScores,
    EndorsementEdge,
    InteractionProofRecord,
    PrincipalProfile,
    StakeSnapshot,
    ValidationAttestation,
    ViolationEvent,
)


BASE_SCORE = 300.0
BEHAVIOR_POINTS = 350.0
STAKE_POINTS = 200.0
ENDORSEMENT_POINTS = 150.0
VALIDATION_POINTS = 150.0
DEVICE_POINTS = 100.0
PRINCIPAL_POINTS = 50.0
VIOLATION_LAMBDA = 4.0
VIOLATION_TAU_DAYS = 180.0
LOW_SAMPLE_THRESHOLD = 10
LOW_STAKE_USD_THRESHOLD = 1_000.0

REASON_LOW_SAMPLE_SIZE = "LOW_SAMPLE_SIZE"
REASON_LOW_STAKE_USD = "LOW_STAKE_USD"
REASON_HIGH_STAKE_CONCENTRATION = "HIGH_STAKE_CONCENTRATION"
REASON_HIGH_VIOLATION_90D = "HIGH_VIOLATION_90D"
REASON_CRITICAL_PRINCIPAL_VIOLATION = "CRITICAL_PRINCIPAL_VIOLATION"
REASON_ENDORSEMENT_CLUSTER_RISK = "ENDORSEMENT_CLUSTER_RISK"
REASON_LOW_VALIDATION_COVERAGE = "LOW_VALIDATION_COVERAGE"
REASON_EXPIRED_PRINCIPAL_VC = "EXPIRED_PRINCIPAL_VC"
REASON_NO_DEVICE_BINDING = "NO_DEVICE_BINDING"
REASON_NETWORK_DRIFT = "NETWORK_DRIFT_WITHOUT_PRINCIPAL_COSIGN"


def calculate_credit_score(payload: CreditInput) -> CreditResult:
    reason_codes: set[str] = set()

    behavior = _behavior_score(payload.interactions, reason_codes)
    stake = _stake_score(payload.stakes, reason_codes)
    endorsement = _endorsement_score(payload.endorsements, reason_codes)
    validation = _validation_score(payload.validations, reason_codes)
    principal = _principal_score(payload.principal, reason_codes)
    device = _device_score(payload.device, reason_codes)
    violation_penalty = _violation_penalty(payload.violations, reason_codes)

    raw_score = (
        BASE_SCORE
        + behavior / 100.0 * BEHAVIOR_POINTS
        + stake / 100.0 * STAKE_POINTS
        + endorsement / 100.0 * ENDORSEMENT_POINTS
        + validation / 100.0 * VALIDATION_POINTS
        + device / 100.0 * DEVICE_POINTS
        + principal / 100.0 * PRINCIPAL_POINTS
        - violation_penalty * VIOLATION_LAMBDA
    )
    score = int(round(_clamp(raw_score, 0.0, 1_000.0)))
    tier = _tier_for_score(score)

    if payload.principal.flagged and score > 599:
        score = 599
        tier = "C"
        reason_codes.add(REASON_CRITICAL_PRINCIPAL_VIOLATION)

    return CreditResult(
        agent_id=payload.agent_id,
        score=score,
        tier=tier,
        dimensions=DimensionScores(
            behavior=round(behavior, 2),
            stake=round(stake, 2),
            endorsement=round(endorsement, 2),
            validation=round(validation, 2),
            device=round(device, 2),
            principal=round(principal, 2),
        ),
        violation_penalty=round(violation_penalty, 2),
        reason_codes=tuple(sorted(reason_codes)),
    )


def _behavior_score(
    interactions: list[InteractionProofRecord],
    reason_codes: set[str],
) -> float:
    dual_signed = [record for record in interactions if record.dual_signed]
    if len(dual_signed) < LOW_SAMPLE_THRESHOLD:
        reason_codes.add(REASON_LOW_SAMPLE_SIZE)
    if not dual_signed:
        return 50.0

    success_rate = _smoothed_rate(
        sum(1 for record in dual_signed if record.success),
        len(dual_signed),
        prior=0.8,
        strength=LOW_SAMPLE_THRESHOLD,
    )
    on_time_rate = _smoothed_rate(
        sum(1 for record in dual_signed if record.on_time),
        len(dual_signed),
        prior=0.8,
        strength=LOW_SAMPLE_THRESHOLD,
    )
    repeat_rate = _repeat_client_rate(dual_signed)

    return _clamp((success_rate * 0.6 + on_time_rate * 0.3 + repeat_rate * 0.1) * 100.0)


def _stake_score(stakes: list[StakeSnapshot], reason_codes: set[str]) -> float:
    weighted_values = [
        max(0.0, stake.usd_value) * max(0.0, stake.weight) * _lock_multiplier(stake)
        for stake in stakes
    ]
    total = sum(weighted_values)
    if total < LOW_STAKE_USD_THRESHOLD:
        reason_codes.add(REASON_LOW_STAKE_USD)
    if total <= 0:
        return 0.0

    dominant_ratio = max(weighted_values) / total
    adjusted_total = total
    if dominant_ratio > 0.8:
        reason_codes.add(REASON_HIGH_STAKE_CONCENTRATION)
        excess = total * (dominant_ratio - 0.8)
        adjusted_total -= excess * 0.5

    return _clamp(math.log10(max(adjusted_total, 1.0) / 100.0) * 25.0)


def _endorsement_score(
    endorsements: list[EndorsementEdge],
    reason_codes: set[str],
) -> float:
    if not endorsements:
        return 0.0

    total_weighted = 0.0
    total_weight = 0.0
    cluster_counts = Counter(edge.cluster_id for edge in endorsements)
    largest_cluster_ratio = max(cluster_counts.values()) / len(endorsements)
    if largest_cluster_ratio > 0.7:
        reason_codes.add(REASON_ENDORSEMENT_CLUSTER_RISK)

    for edge in endorsements:
        cluster_penalty = 0.5 if cluster_counts[edge.cluster_id] / len(endorsements) > 0.7 else 1.0
        weight = cluster_penalty
        total_weighted += _clamp(edge.score) * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0
    return _clamp(total_weighted / total_weight)


VALIDATION_TYPE_WEIGHTS = {"tee": 60.0, "re_execution": 80.0, "zkml": 100.0}


def _validation_score(
    validations: list[ValidationAttestation],
    reason_codes: set[str],
) -> float:
    passed_by_validator: dict[str, float] = {}

    for attestation in validations:
        if not attestation.passed:
            continue
        weight = VALIDATION_TYPE_WEIGHTS.get(attestation.validation_type)
        if weight is None:
            continue
        current = passed_by_validator.get(attestation.validator_id, 0.0)
        passed_by_validator[attestation.validator_id] = max(current, weight)

    if not passed_by_validator:
        reason_codes.add(REASON_LOW_VALIDATION_COVERAGE)
        return 0.0

    score = sum(passed_by_validator.values()) / len(passed_by_validator)
    if len(passed_by_validator) < 2:
        reason_codes.add(REASON_LOW_VALIDATION_COVERAGE)
        score *= 0.85
    return _clamp(score)


def _device_score(
    device,
    reason_codes: set[str],
) -> float:
    level_scores = {"strong": 100.0, "runtime": 75.0, "registration": 50.0, "none": 0.0}
    score = level_scores.get(device.binding_level, 0.0)
    if device.binding_level == "none":
        reason_codes.add(REASON_NO_DEVICE_BINDING)
    if device.has_network_drift and not device.has_principal_co_sign:
        score = _clamp(score - 50.0)
        reason_codes.add(REASON_NETWORK_DRIFT)
    return score


def _principal_score(
    principal: PrincipalProfile,
    reason_codes: set[str],
) -> float:
    if principal.vc_expired:
        reason_codes.add(REASON_EXPIRED_PRINCIPAL_VC)
        return 0.0
    if principal.flagged:
        reason_codes.add(REASON_CRITICAL_PRINCIPAL_VIOLATION)
        return 0.0
    return _clamp(principal.score / 1_000.0 * 100.0 * 0.3)


def _violation_penalty(violations: list[ViolationEvent], reason_codes: set[str]) -> float:
    recent_count = sum(1 for violation in violations if violation.days_ago <= 90)
    if recent_count >= 3:
        reason_codes.add(REASON_HIGH_VIOLATION_90D)

    penalty = 0.0
    for violation in violations:
        penalty += violation.severity * math.exp(-violation.days_ago / VIOLATION_TAU_DAYS)
        if violation.severity >= 71:
            reason_codes.add(REASON_CRITICAL_PRINCIPAL_VIOLATION)
    return penalty


def _repeat_client_rate(interactions: list[InteractionProofRecord]) -> float:
    counts: dict[str, int] = defaultdict(int)
    for record in interactions:
        counts[record.client_id] += 1
    repeat_interactions = sum(count for count in counts.values() if count > 1)
    return repeat_interactions / len(interactions)


def _smoothed_rate(successes: int, total: int, prior: float, strength: int) -> float:
    return (successes + prior * strength) / (total + strength)


def _lock_multiplier(stake: StakeSnapshot) -> float:
    if stake.lock_days_remaining >= 30:
        return 1.0
    if stake.lock_days_remaining <= 0:
        return 0.5
    return 0.5 + stake.lock_days_remaining / 60.0


def _tier_for_score(score: int) -> str:
    if score >= 900:
        return "S"
    if score >= 750:
        return "A"
    if score >= 600:
        return "B"
    if score >= 400:
        return "C"
    return "D"


def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))
