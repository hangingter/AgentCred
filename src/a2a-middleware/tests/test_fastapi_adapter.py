from datetime import datetime, timedelta, timezone
import unittest

from fastapi.testclient import TestClient

from agent_score_engine import (
    CreditInput,
    DeviceProfile,
    InteractionProofRecord,
    PrincipalProfile,
    StakeSnapshot,
    ValidationAttestation,
    build_credit_vc,
    calculate_credit_score,
    sign_credit_vc,
)
from agent_score_middleware import AgentCard, AgentPolicy, create_agent_app


ISSUER = "did:ethr:0x2105:0xissuer"
SECRET = "issuer-secret"


class FastAPIAdapterTest(unittest.TestCase):
    def test_get_agent_card(self) -> None:
        client = TestClient(_provider_app())

        response = client.get("/agent-card")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["name"], "provider")
        self.assertIn("x-agent-score", body)
        self.assertIn("credit_vc", body["x-agent-score"])

    def test_valid_caller_can_invoke_a2a(self) -> None:
        client = TestClient(_provider_app())
        caller_card = _card("caller").to_a2a_dict()

        response = client.post(
            "/a2a",
            json={
                "caller_card": _http_card_payload(caller_card),
                "task": {"task_id": "task-1", "prompt": "run risk check"},
                "caller_signature": "caller-sig-1",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["handshake"]["accepted"])
        self.assertEqual(body["result"]["status"], "completed")
        self.assertEqual(len(body["ipr"]["hash"]), 64)
        self.assertEqual(body["ipr"]["caller_signature"], "caller-sig-1")

    def test_untrusted_issuer_gets_403(self) -> None:
        client = TestClient(_provider_app(trusted_issuers={"did:bad"}))
        caller_card = _card("caller").to_a2a_dict()

        response = client.post(
            "/a2a",
            json={
                "caller_card": _http_card_payload(caller_card),
                "task": {"task_id": "task-1", "prompt": "run risk check"},
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"]["reason"], "UNTRUSTED_ISSUER")

    def test_unknown_proof_type_gets_403(self) -> None:
        client = TestClient(_provider_app())
        caller_card = _card("caller")
        card_dict = caller_card.to_a2a_dict()
        card_dict["x-agent-score"]["credit_vc"]["proof"]["type"] = "UnknownProofType"

        response = client.post(
            "/a2a",
            json={
                "caller_card": _http_card_payload(card_dict),
                "task": {"task_id": "task-1"},
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"]["reason"], "INVALID_CREDIT_VC")

    def test_missing_caller_signature_gets_400(self) -> None:
        client = TestClient(_provider_app())
        caller_card = _card("caller").to_a2a_dict()

        response = client.post(
            "/a2a",
            json={
                "caller_card": _http_card_payload(caller_card),
                "task": {"task_id": "task-1"},
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"]["reason"], "MISSING_CALLER_SIGNATURE")

    def test_valid_caller_with_signature_gets_200(self) -> None:
        client = TestClient(_provider_app())
        caller_card = _card("caller").to_a2a_dict()

        response = client.post(
            "/a2a",
            json={
                "caller_card": _http_card_payload(caller_card),
                "task": {"task_id": "task-1", "prompt": "run risk check"},
                "caller_signature": "caller-signed-unsigned-ipr",
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body["handshake"]["accepted"])
        self.assertEqual(body["ipr"]["caller_signature"], "caller-signed-unsigned-ipr")


def _provider_app(trusted_issuers=None):
    provider_card = _card("provider")
    policy = AgentPolicy(
        min_credit_score=600,
        min_tier="B",
        trusted_issuers=trusted_issuers if trusted_issuers is not None else {ISSUER},
    )
    return create_agent_app(
        provider_card=provider_card,
        provider_secret="provider-secret",
        policy=policy,
        secret_by_issuer={ISSUER: SECRET},
        task_handler=lambda task: {
            "task_id": task["task_id"],
            "status": "completed",
            "answer": f"handled {task.get('prompt', '')}",
        },
    )


def _card(name: str) -> AgentCard:
    did = f"did:ethr:0x2105:0x{name}"
    credit_input = CreditInput(
        agent_id=did,
        interactions=[
            InteractionProofRecord(client_id=f"peer-{index % 3}", success=True, on_time=True)
            for index in range(12)
        ],
        stakes=[
            StakeSnapshot(asset="USDC", usd_value=2_000),
            StakeSnapshot(asset="WETH", usd_value=2_000),
        ],
        validations=[
            ValidationAttestation(validator_id="tee-lab", validation_type="tee"),
            ValidationAttestation(validator_id="re-lab", validation_type="re_execution"),
            ValidationAttestation(validator_id="zk-lab", validation_type="zkml"),
        ],
        principal=PrincipalProfile(score=900),
        device=DeviceProfile(binding_level="strong"),
    )
    score = calculate_credit_score(credit_input)
    issued_at = datetime.now(timezone.utc) - timedelta(days=1)
    payload = build_credit_vc(score, issuer=ISSUER, issued_at=issued_at)
    signed = sign_credit_vc(payload, issuer=ISSUER, secret=SECRET, proof_created=issued_at)
    return AgentCard(
        name=name,
        version="0.1.0",
        endpoint=f"local://{name}/a2a",
        skills=["risk-check"],
        did=did,
        principal=f"did:web:{name}.example",
        credit_vc=signed,
    )


def _http_card_payload(card_dict):
    extension = card_dict["x-agent-score"]
    return {
        "name": card_dict["name"],
        "version": card_dict["version"],
        "endpoint": card_dict["endpoints"]["a2a"],
        "skills": card_dict["skills"],
        "did": extension["did"],
        "principal": extension["principal"],
        "credit_vc": extension["credit_vc"],
    }


if __name__ == "__main__":
    unittest.main()
