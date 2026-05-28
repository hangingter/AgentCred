import unittest

from agent_score_engine import CreditInput, PrincipalProfile
from agents import LocalAgent
from demo import AUTHORITY_ISSUER, AUTHORITY_SECRET, _build_provider_agent, run_demo
from protocol import AgentPolicy, verify_agent_card_credit


class MVPProtocolDemoTest(unittest.TestCase):
    def test_valid_provider_passes_handshake(self) -> None:
        provider = _build_provider_agent()
        card = provider.agent_card()
        policy = AgentPolicy(
            min_credit_score=600,
            min_tier="B",
            trusted_issuers={AUTHORITY_ISSUER},
        )

        result = verify_agent_card_credit(
            card,
            policy,
            secret_by_issuer={AUTHORITY_ISSUER: AUTHORITY_SECRET},
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.reason, "ACCEPTED")
        self.assertGreaterEqual(result.score, 600)

    def test_untrusted_issuer_fails_handshake(self) -> None:
        provider = _build_provider_agent()
        card = provider.agent_card()
        policy = AgentPolicy(
            min_credit_score=600,
            min_tier="B",
            trusted_issuers={"did:ethr:0x2105:0xBAD"},
        )

        result = verify_agent_card_credit(
            card,
            policy,
            secret_by_issuer={AUTHORITY_ISSUER: AUTHORITY_SECRET},
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "UNTRUSTED_ISSUER")

    def test_score_below_policy_fails_handshake(self) -> None:
        weak_provider = LocalAgent(
            name="weak-provider",
            did="did:ethr:0x2105:0xweak",
            principal="did:web:weak.example",
            endpoint="local://weak/a2a",
            skills=["risk-check"],
            initial_credit_input=CreditInput(
                agent_id="weak",
                principal=PrincipalProfile(score=100),
            ),
            authority_issuer=AUTHORITY_ISSUER,
            authority_secret=AUTHORITY_SECRET,
            agent_secret="weak-secret",
        )
        policy = AgentPolicy(
            min_credit_score=900,
            min_tier="S",
            trusted_issuers={AUTHORITY_ISSUER},
        )

        result = verify_agent_card_credit(
            weak_provider.agent_card(),
            policy,
            secret_by_issuer={AUTHORITY_ISSUER: AUTHORITY_SECRET},
        )

        self.assertFalse(result.accepted)
        self.assertIn(result.reason, {"SCORE_BELOW_THRESHOLD", "TIER_BELOW_THRESHOLD"})

    def test_demo_run_returns_ipr_hash_and_score_delta(self) -> None:
        summary = run_demo(print_output=False)

        self.assertTrue(summary["handshake"]["accepted"])
        self.assertEqual(summary["task_result"]["status"], "completed")
        self.assertEqual(len(summary["ipr"]["hash"]), 64)
        self.assertIn("before", summary["score_delta"])
        self.assertIn("after", summary["score_delta"])
        self.assertGreaterEqual(summary["score_delta"]["after"], 0)


if __name__ == "__main__":
    unittest.main()
