from datetime import datetime, timedelta, timezone
import unittest

from agent_score_engine import (
    CreditInput,
    InteractionProofRecord,
    PrincipalProfile,
    StakeSnapshot,
    ValidationAttestation,
    build_credit_vc,
    calculate_credit_score,
    sign_credit_vc,
    verify_credit_vc,
)


class CreditVCTest(unittest.TestCase):
    def test_build_credit_vc_uses_30_day_validity(self) -> None:
        result = calculate_credit_score(_sample_input())
        issued_at = datetime(2026, 5, 27, 12, 0, 0, tzinfo=timezone.utc)

        vc = build_credit_vc(
            result,
            issuer="did:ethr:0x2105:0xissuer",
            issued_at=issued_at,
            snapshot_root="0xabc",
            violation_count_90d=1,
        )

        self.assertEqual(vc["issuer"], "did:ethr:0x2105:0xissuer")
        self.assertEqual(vc["validFrom"], "2026-05-27T12:00:00Z")
        self.assertEqual(vc["validUntil"], "2026-06-26T12:00:00Z")
        self.assertEqual(vc["credentialSubject"]["id"], "did:ethr:0x2105:0xagent")
        self.assertEqual(vc["credentialSubject"]["snapshot_root"], "0xabc")
        self.assertEqual(vc["credentialSubject"]["violation_count_90d"], 1)

    def test_sign_and_verify_credit_vc(self) -> None:
        result = calculate_credit_score(_sample_input())
        issued_at = datetime(2026, 5, 27, 12, 0, 0, tzinfo=timezone.utc)
        issuer = "did:ethr:0x2105:0xissuer"
        vc = build_credit_vc(result, issuer=issuer, issued_at=issued_at)
        signed = sign_credit_vc(vc, issuer=issuer, secret="secret", proof_created=issued_at)

        self.assertIn("proof", signed)
        self.assertTrue(
            verify_credit_vc(
                signed,
                trusted_issuers={issuer},
                secret_by_issuer={issuer: "secret"},
                now=issued_at + timedelta(days=1),
            )
        )

    def test_verify_rejects_untrusted_expired_or_tampered_vc(self) -> None:
        result = calculate_credit_score(_sample_input())
        issued_at = datetime(2026, 5, 27, 12, 0, 0, tzinfo=timezone.utc)
        issuer = "did:ethr:0x2105:0xissuer"
        signed = sign_credit_vc(
            build_credit_vc(result, issuer=issuer, issued_at=issued_at),
            issuer=issuer,
            secret="secret",
            proof_created=issued_at,
        )

        self.assertFalse(
            verify_credit_vc(
                signed,
                trusted_issuers={"did:ethr:0x2105:0xother"},
                secret_by_issuer={issuer: "secret"},
                now=issued_at + timedelta(days=1),
            )
        )
        self.assertFalse(
            verify_credit_vc(
                signed,
                trusted_issuers={issuer},
                secret_by_issuer={issuer: "secret"},
                now=issued_at + timedelta(days=31),
            )
        )

        tampered = dict(signed)
        tampered["credentialSubject"] = dict(signed["credentialSubject"])
        tampered["credentialSubject"]["score"] = 1_000
        self.assertFalse(
            verify_credit_vc(
                tampered,
                trusted_issuers={issuer},
                secret_by_issuer={issuer: "secret"},
                now=issued_at + timedelta(days=1),
            )
        )


def _sample_input() -> CreditInput:
    return CreditInput(
        agent_id="did:ethr:0x2105:0xagent",
        interactions=[
            InteractionProofRecord(client_id=f"client-{index % 5}", success=True, on_time=True)
            for index in range(12)
        ],
        stakes=[StakeSnapshot(asset="USDC", usd_value=2_000)],
        validations=[ValidationAttestation(validator_id="validator", validation_type="tee")],
        principal=PrincipalProfile(score=800),
    )


if __name__ == "__main__":
    unittest.main()
