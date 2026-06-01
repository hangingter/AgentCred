import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import DEFAULT_SECRET_ENV, app


class CreditEngineAPITest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_and_schemas(self) -> None:
        health = self.client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.json(), {"status": "ok"})

        schemas = self.client.get("/schemas")
        self.assertEqual(schemas.status_code, 200)
        body = schemas.json()
        self.assertIn("InteractionProofRecord", body)
        self.assertIn("CreditVC", body)

    def test_score_endpoint(self) -> None:
        response = self.client.post("/score", json=_sample_payload())

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["agent_id"], "did:ethr:0x2105:0xagent")
        self.assertGreaterEqual(body["score"], 0)
        self.assertLessEqual(body["score"], 1000)
        self.assertIn(body["tier"], ["S", "A", "B", "C", "D"])
        self.assertIn("dimensions", body)
        self.assertGreater(body["dimensions"]["device"], 0)

    def test_issue_vc_requires_secret(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            response = self.client.post("/issue-vc", json={"credit_input": _sample_payload()})

        self.assertEqual(response.status_code, 500)
        self.assertIn(DEFAULT_SECRET_ENV, response.json()["detail"])

    def test_issue_vc_endpoint(self) -> None:
        with patch.dict(os.environ, {DEFAULT_SECRET_ENV: "local-secret"}, clear=True):
            response = self.client.post(
                "/issue-vc",
                json={
                    "credit_input": _sample_payload(),
                    "issuer": "did:ethr:0x2105:0xissuer",
                    "snapshot_root": "0xabc",
                    "violation_count_90d": 0,
                    "issued_at": "2026-05-27T12:00:00Z",
                },
            )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["issuer"], "did:ethr:0x2105:0xissuer")
        self.assertEqual(body["validFrom"], "2026-05-27T12:00:00Z")
        self.assertEqual(body["validUntil"], "2026-06-26T12:00:00Z")
        self.assertEqual(body["credentialSubject"]["snapshot_root"], "0xabc")
        self.assertIn("proof", body)
        self.assertIn("jws", body["proof"])


def _sample_payload() -> dict:
    return {
        "agent_id": "did:ethr:0x2105:0xagent",
        "interactions": [
            {"client_id": f"client-{index % 3}", "success": True, "on_time": True}
            for index in range(12)
        ],
        "stakes": [{"asset": "USDC", "usd_value": 2_000, "weight": 1.0}],
        "violations": [],
        "endorsements": [{"endorser_id": "endorser", "score": 80, "cluster_id": "finance"}],
        "validations": [{"validator_id": "validator", "validation_type": "tee", "passed": True}],
        "principal": {"score": 800, "flagged": False, "vc_expired": False},
        "device": {
            "binding_level": "strong",
            "attestation": {
                "attestation_type": "tee_sgx_ecdsa_qe3",
                "device_pubkey_hash": "0xabc",
                "agent_did": "did:ethr:0x2105:0xagent",
                "timestamp": 1779984000,
                "quote": "demo-quote",
                "signature": "demo-signature",
            },
            "network": {"country_code": "SG", "asn": 12345},
            "registered_country_code": "SG",
            "registered_asn": 12345,
        },
    }


if __name__ == "__main__":
    unittest.main()
