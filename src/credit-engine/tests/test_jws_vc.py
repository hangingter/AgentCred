from datetime import datetime, timedelta, timezone
import unittest

from agent_score_engine import (
    CreditInput,
    PrincipalProfile,
    build_credit_vc,
    calculate_credit_score,
    generate_es256k_private_key_pem,
    public_key_pem_from_private_key,
    sign_credit_vc_jws,
    verify_credit_vc_jws,
)


class JwsVCTest(unittest.TestCase):
    def test_sign_and_verify_jws_credit_vc(self) -> None:
        issuer = "did:ethr:0x2105:0xissuer"
        private_key = generate_es256k_private_key_pem()
        public_key = public_key_pem_from_private_key(private_key)
        score = calculate_credit_score(
            CreditInput(agent_id="did:agent", principal=PrincipalProfile(score=800))
        )
        issued_at = datetime.now(timezone.utc) - timedelta(days=1)
        vc = build_credit_vc(score, issuer=issuer, issued_at=issued_at)
        signed = sign_credit_vc_jws(vc, issuer=issuer, private_key_pem=private_key)

        self.assertTrue(verify_credit_vc_jws(signed, {issuer}, {issuer: public_key}))
        self.assertEqual(signed["proof"]["type"], "AgentScoreJWS2026")

    def test_jws_rejects_tampered_payload(self) -> None:
        issuer = "did:ethr:0x2105:0xissuer"
        private_key = generate_es256k_private_key_pem()
        public_key = public_key_pem_from_private_key(private_key)
        score = calculate_credit_score(
            CreditInput(agent_id="did:agent", principal=PrincipalProfile(score=800))
        )
        issued_at = datetime.now(timezone.utc) - timedelta(days=1)
        signed = sign_credit_vc_jws(
            build_credit_vc(score, issuer=issuer, issued_at=issued_at),
            issuer=issuer,
            private_key_pem=private_key,
        )
        signed["credentialSubject"]["score"] = 999

        self.assertFalse(verify_credit_vc_jws(signed, {issuer}, {issuer: public_key}))

    def test_jws_rejects_revoked_credential_status(self) -> None:
        issuer = "did:ethr:0x2105:0xissuer"
        private_key = generate_es256k_private_key_pem()
        public_key = public_key_pem_from_private_key(private_key)
        score = calculate_credit_score(
            CreditInput(agent_id="did:agent", principal=PrincipalProfile(score=800))
        )
        issued_at = datetime.now(timezone.utc) - timedelta(days=1)
        vc = build_credit_vc(
            score,
            issuer=issuer,
            issued_at=issued_at,
            credential_status={
                "id": "agentcred:revocation:credit:1",
                "type": "AgentCredRevocationList2026",
            },
        )
        signed = sign_credit_vc_jws(vc, issuer=issuer, private_key_pem=private_key)

        self.assertFalse(
            verify_credit_vc_jws(
                signed,
                {issuer},
                {issuer: public_key},
                revoked_status_ids={"agentcred:revocation:credit:1"},
            )
        )

    def test_jws_rejects_wrong_kid_or_alg(self) -> None:
        issuer = "did:ethr:0x2105:0xissuer"
        other_issuer = "did:ethr:0x2105:0xother"
        private_key = generate_es256k_private_key_pem()
        public_key = public_key_pem_from_private_key(private_key)
        score = calculate_credit_score(
            CreditInput(agent_id="did:agent", principal=PrincipalProfile(score=800))
        )
        issued_at = datetime.now(timezone.utc) - timedelta(days=1)
        signed = sign_credit_vc_jws(
            build_credit_vc(score, issuer=issuer, issued_at=issued_at),
            issuer=issuer,
            private_key_pem=private_key,
        )

        self.assertFalse(verify_credit_vc_jws(signed, {other_issuer}, {other_issuer: public_key}))

        tampered_kid = signed["proof"]["jws"].split(".")
        import json, base64
        header = json.loads(base64.urlsafe_b64decode(tampered_kid[0] + "==").decode("utf-8"))
        header["kid"] = other_issuer
        tampered_kid[0] = base64.urlsafe_b64encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")).decode("ascii").rstrip("=")
        signed["proof"]["jws"] = ".".join(tampered_kid)
        self.assertFalse(verify_credit_vc_jws(signed, {issuer}, {issuer: public_key}))

        header["alg"] = "ES256"
        tampered_alg = [
            base64.urlsafe_b64encode(json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")).decode("ascii").rstrip("="),
            tampered_kid[1],
            tampered_kid[2],
        ]
        signed["proof"]["jws"] = ".".join(tampered_alg)
        self.assertFalse(verify_credit_vc_jws(signed, {issuer}, {issuer: public_key}))


if __name__ == "__main__":
    unittest.main()
