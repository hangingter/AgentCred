import unittest

from agent_score_engine import (
    CreditInput,
    CreditResult,
    DeviceProfile,
    EndorsementEdge,
    InteractionProofRecord,
    PrincipalProfile,
    StakeSnapshot,
    ValidationAttestation,
    ViolationEvent,
    calculate_credit_score,
)


class CreditScoringTest(unittest.TestCase):
    def test_strong_agent_reaches_s_tier_without_reason_codes(self) -> None:
        payload = CreditInput(
            agent_id="agent-1",
            interactions=[
                InteractionProofRecord(client_id=f"client-{index % 6}", success=True, on_time=True)
                for index in range(24)
            ],
            stakes=[
                StakeSnapshot(asset="USDC", usd_value=8_000, weight=1.0, lock_days_remaining=90),
                StakeSnapshot(asset="ETH", usd_value=3_000, weight=0.9, lock_days_remaining=90),
            ],
            endorsements=[
                EndorsementEdge(endorser_id="a", score=90, cluster_id="finance"),
                EndorsementEdge(endorser_id="b", score=82, cluster_id="infra"),
                EndorsementEdge(endorser_id="c", score=88, cluster_id="commerce"),
            ],
            validations=[
                ValidationAttestation(validator_id="tee-lab", validation_type="tee"),
                ValidationAttestation(validator_id="zk-lab", validation_type="zkml"),
            ],
            principal=PrincipalProfile(score=900, flagged=False, vc_expired=False),
            device=DeviceProfile(binding_level="strong"),
        )

        result = calculate_credit_score(payload)

        self.assertEqual(result.tier, "S")
        self.assertGreaterEqual(result.score, 900)
        self.assertEqual(result.reason_codes, ())
        self.assertGreater(result.dimensions.behavior, 90)
        self.assertGreater(result.dimensions.validation, 75)
        self.assertGreater(result.dimensions.device, 90)

    def test_low_sample_and_low_stake_emit_reason_codes(self) -> None:
        payload = CreditInput(
            agent_id="agent-2",
            interactions=[
                InteractionProofRecord(client_id="client-a", success=True, on_time=False),
                InteractionProofRecord(client_id="client-b", success=False, on_time=False),
            ],
            stakes=[StakeSnapshot(asset="USDC", usd_value=100, weight=1.0, lock_days_remaining=10)],
        )

        result = calculate_credit_score(payload)

        self.assertIn("LOW_SAMPLE_SIZE", result.reason_codes)
        self.assertIn("LOW_STAKE_USD", result.reason_codes)
        self.assertIn("LOW_VALIDATION_COVERAGE", result.reason_codes)
        self.assertLess(result.score, 650)

    def test_stake_concentration_reduces_stake_dimension(self) -> None:
        diversified = CreditInput(
            agent_id="agent-diversified",
            stakes=[
                StakeSnapshot(asset="USDC", usd_value=5_000, weight=1.0),
                StakeSnapshot(asset="ETH", usd_value=5_000, weight=1.0),
            ],
        )
        concentrated = CreditInput(
            agent_id="agent-concentrated",
            stakes=[
                StakeSnapshot(asset="USDC", usd_value=9_500, weight=1.0),
                StakeSnapshot(asset="ETH", usd_value=500, weight=1.0),
            ],
        )

        diversified_result = calculate_credit_score(diversified)
        concentrated_result = calculate_credit_score(concentrated)

        self.assertIn("HIGH_STAKE_CONCENTRATION", concentrated_result.reason_codes)
        self.assertLess(concentrated_result.dimensions.stake, diversified_result.dimensions.stake)

    def test_critical_principal_violation_caps_tier_to_c(self) -> None:
        payload = CreditInput(
            agent_id="agent-flagged",
            interactions=[
                InteractionProofRecord(client_id=f"client-{index % 4}", success=True, on_time=True)
                for index in range(20)
            ],
            stakes=[
                StakeSnapshot(asset="USDC", usd_value=20_000, weight=1.0),
                StakeSnapshot(asset="ETH", usd_value=10_000, weight=1.0),
            ],
            endorsements=[
                EndorsementEdge(endorser_id="a", score=95, cluster_id="finance"),
                EndorsementEdge(endorser_id="b", score=95, cluster_id="infra"),
            ],
            validations=[
                ValidationAttestation(validator_id="tee-lab", validation_type="tee"),
                ValidationAttestation(validator_id="zk-lab", validation_type="zkml"),
            ],
            principal=PrincipalProfile(score=950, flagged=True, vc_expired=False),
        )

        result = calculate_credit_score(payload)

        self.assertEqual(result.score, 599)
        self.assertEqual(result.tier, "C")
        self.assertIn("CRITICAL_PRINCIPAL_VIOLATION", result.reason_codes)

    def test_recent_violations_apply_decay_penalty(self) -> None:
        clean = CreditInput(
            agent_id="clean",
            violations=[],
            principal=PrincipalProfile(score=800),
        )
        risky = CreditInput(
            agent_id="risky",
            violations=[
                ViolationEvent(severity=30, days_ago=10),
                ViolationEvent(severity=40, days_ago=20),
                ViolationEvent(severity=80, days_ago=30),
            ],
            principal=PrincipalProfile(score=800),
        )

        clean_result = calculate_credit_score(clean)
        risky_result = calculate_credit_score(risky)

        self.assertLess(risky_result.score, clean_result.score)
        self.assertGreater(risky_result.violation_penalty, 100)
        self.assertIn("HIGH_VIOLATION_90D", risky_result.reason_codes)
        self.assertIn("CRITICAL_PRINCIPAL_VIOLATION", risky_result.reason_codes)

    def test_unknown_validation_type_is_ignored_not_keyerror(self) -> None:
        baseline = CreditInput(
            agent_id="agent-1",
        )
        with_unknown = CreditInput(
            agent_id="agent-1",
            validations=[
                ValidationAttestation(validator_id="tee-lab", validation_type="tee"),
                ValidationAttestation(validator_id="unknown-lab", validation_type="unknown_type"),
            ],
        )
        baseline_result = calculate_credit_score(baseline)
        with_unknown_result = calculate_credit_score(with_unknown)
        self.assertIsInstance(with_unknown_result.score, int)
        self.assertIsInstance(baseline_result.score, int)


if __name__ == "__main__":
    unittest.main()
