from datetime import datetime, timedelta, timezone
import unittest

from agent_score_engine import (
    CreditInput,
    DeviceProfile,
    InteractionProofRecord,
    PrincipalProfile,
    StakeSnapshot,
    ValidationAttestation,
    build_credit_vc,
    calculate_credit_score,
    generate_es256k_private_key_pem,
    public_key_pem_from_private_key,
    sign_credit_vc_jws,
    sign_credit_vc,
)
from agent_score_middleware import (
    AgentCard,
    AgentPolicy,
    InteractionProofRecordEnvelope,
    sha256_json,
    sign_payload,
    verify_agent_card_credit,
)


ISSUER = "did:ethr:0x2105:0xissuer"
SECRET = "issuer-secret"


class AgentScoreMiddlewareTest(unittest.TestCase):
    def test_valid_agent_card_passes_handshake(self) -> None:
        card = _card_with_score()
        policy = AgentPolicy(min_credit_score=600, min_tier="B", trusted_issuers={ISSUER})

        result = verify_agent_card_credit(card, policy, {ISSUER: SECRET})

        self.assertTrue(result.accepted)
        self.assertEqual(result.reason, "ACCEPTED")
        self.assertEqual(result.agent_did, card.did)
        self.assertIsNotNone(result.score)
        self.assertIsNotNone(result.tier)

    def test_policy_rejects_untrusted_issuer(self) -> None:
        card = _card_with_score()
        policy = AgentPolicy(min_credit_score=600, min_tier="B", trusted_issuers={"did:bad"})

        result = verify_agent_card_credit(card, policy, {ISSUER: SECRET})

        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "UNTRUSTED_ISSUER")

    def test_policy_rejects_low_score(self) -> None:
        card = _card_with_score(principal_score=100)
        policy = AgentPolicy(min_credit_score=950, min_tier="S", trusted_issuers={ISSUER})

        result = verify_agent_card_credit(card, policy, {ISSUER: SECRET})

        self.assertFalse(result.accepted)
        self.assertIn(result.reason, {"SCORE_BELOW_THRESHOLD", "TIER_BELOW_THRESHOLD"})

    def test_ipr_hash_excludes_signatures(self) -> None:
        unsigned = {
            "caller_did": "did:caller",
            "callee_did": "did:callee",
            "task_id": "task-1",
            "success": True,
            "on_time": True,
            "result_hash": sha256_json({"ok": True}),
        }
        ipr = InteractionProofRecordEnvelope(
            **unsigned,
            caller_signature=sign_payload(unsigned, "caller-secret"),
            callee_signature=sign_payload(unsigned, "callee-secret"),
        )
        mutated = InteractionProofRecordEnvelope(
            **unsigned,
            caller_signature="changed",
            callee_signature="changed",
        )

        self.assertEqual(ipr.ipr_hash, mutated.ipr_hash)
        self.assertEqual(len(ipr.ipr_hash), 64)

    def test_jws_credit_vc_passes_handshake(self) -> None:
        private_key = generate_es256k_private_key_pem()
        public_key = public_key_pem_from_private_key(private_key)
        card = _card_with_score(private_key_pem=private_key)
        policy = AgentPolicy(min_credit_score=600, min_tier="B", trusted_issuers={ISSUER})

        result = verify_agent_card_credit(
            card,
            policy,
            {},
            public_key_by_issuer={ISSUER: public_key},
        )

        self.assertTrue(result.accepted)
        self.assertEqual(result.reason, "ACCEPTED")

    def test_strong_device_binding_passes(self) -> None:
        device_authority = "did:web:device.example"
        device_private = generate_es256k_private_key_pem()
        device_public = public_key_pem_from_private_key(device_private)
        base_card = _card_with_score()
        device_vc = _device_binding_vc(
            base_card.did,
            binding_level="strong",
            country="SG",
            asn=12345,
            issuer=device_authority,
            private_key_pem=device_private,
        )
        card = AgentCard(
            name=base_card.name,
            version=base_card.version,
            endpoint=base_card.endpoint,
            skills=list(base_card.skills),
            did=base_card.did,
            principal=base_card.principal,
            credit_vc=base_card.credit_vc,
            device_binding_vc=device_vc,
            network_fingerprint={"country_code": "SG", "asn": 12345},
        )

        policy = AgentPolicy(
            min_credit_score=600,
            min_tier="B",
            trusted_issuers={ISSUER},
            require_device_binding=True,
            min_binding_level="strong",
            trusted_device_authorities={device_authority},
            allowed_countries={"SG"},
        )
        result = verify_agent_card_credit(
            card,
            policy,
            {ISSUER: SECRET},
            public_key_by_device_authority={device_authority: device_public},
        )
        self.assertTrue(result.accepted)
        self.assertEqual(result.reason, "ACCEPTED")

    def test_missing_device_binding_rejected(self) -> None:
        card = _card_with_score()
        policy = AgentPolicy(
            min_credit_score=600,
            min_tier="B",
            trusted_issuers={ISSUER},
            require_device_binding=True,
            trusted_device_authorities={"did:web:device.example"},
        )
        result = verify_agent_card_credit(card, policy, {ISSUER: SECRET})
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "MISSING_DEVICE_BINDING")

    def test_network_drift_without_cosign_rejected(self) -> None:
        device_authority = "did:web:device.example"
        device_private = generate_es256k_private_key_pem()
        device_public = public_key_pem_from_private_key(device_private)
        base_card = _card_with_score()
        card = AgentCard(
            name=base_card.name,
            version=base_card.version,
            endpoint=base_card.endpoint,
            skills=list(base_card.skills),
            did=base_card.did,
            principal=base_card.principal,
            credit_vc=base_card.credit_vc,
            device_binding_vc=_device_binding_vc(
                base_card.did, "strong", "SG", 12345, device_authority, device_private),
            network_fingerprint={"country_code": "US", "asn": 12345},
        )

        policy = AgentPolicy(
            min_credit_score=600,
            min_tier="B",
            trusted_issuers={ISSUER},
            require_device_binding=True,
            trusted_device_authorities={device_authority},
            allowed_countries={"SG", "US"},
            require_principal_co_sign_on_drift=True,
        )
        result = verify_agent_card_credit(
            card, policy, {ISSUER: SECRET}, public_key_by_device_authority={device_authority: device_public})
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "NETWORK_DRIFT_WITHOUT_PRINCIPAL_COSIGN")

    def test_network_drift_with_cosign_accepted(self) -> None:
        device_authority = "did:web:device.example"
        device_private = generate_es256k_private_key_pem()
        device_public = public_key_pem_from_private_key(device_private)
        base_card = _card_with_score()
        card = AgentCard(
            name=base_card.name,
            version=base_card.version,
            endpoint=base_card.endpoint,
            skills=list(base_card.skills),
            did=base_card.did,
            principal=base_card.principal,
            credit_vc=base_card.credit_vc,
            device_binding_vc=_device_binding_vc(
                base_card.did, "strong", "SG", 12345, device_authority, device_private),
            network_fingerprint={"country_code": "US", "asn": 12345, "principal_co_signature": "principal-signed"},
        )

        policy = AgentPolicy(
            min_credit_score=600,
            min_tier="B",
            trusted_issuers={ISSUER},
            require_device_binding=True,
            trusted_device_authorities={device_authority},
            allowed_countries={"SG", "US"},
            require_principal_co_sign_on_drift=True,
        )
        result = verify_agent_card_credit(
            card, policy, {ISSUER: SECRET}, public_key_by_device_authority={device_authority: device_public})
        self.assertTrue(result.accepted)

    def test_device_score_improves_credit_score(self) -> None:
        from agent_score_engine import CreditInput, DeviceProfile, calculate_credit_score

        no_device = calculate_credit_score(CreditInput(agent_id="agent-1"))
        with_device = calculate_credit_score(CreditInput(
            agent_id="agent-1",
            device=DeviceProfile(binding_level="strong"),
        ))
        self.assertGreater(with_device.score, no_device.score)
        self.assertIn("NO_DEVICE_BINDING", no_device.reason_codes)
        self.assertNotIn("NO_DEVICE_BINDING", with_device.reason_codes)


def _card_with_score(principal_score: int = 800, private_key_pem: str = "") -> AgentCard:
    credit_input = CreditInput(
        agent_id="did:ethr:0x2105:0xagent",
        interactions=[
            InteractionProofRecord(client_id=f"client-{index % 3}", success=True, on_time=True)
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
        principal=PrincipalProfile(score=principal_score),
        device=DeviceProfile(binding_level="strong"),
    )
    result = calculate_credit_score(credit_input)
    issued_at = datetime.now(timezone.utc) - timedelta(days=1)
    payload = build_credit_vc(result, issuer=ISSUER, issued_at=issued_at)
    if private_key_pem:
        signed = sign_credit_vc_jws(payload, issuer=ISSUER, private_key_pem=private_key_pem)
    else:
        signed = sign_credit_vc(payload, issuer=ISSUER, secret=SECRET, proof_created=issued_at)
    return AgentCard(
        name="provider",
        version="0.1.0",
        endpoint="local://provider/a2a",
        skills=["risk-check"],
        did="did:ethr:0x2105:0xagent",
        principal="did:web:provider.example",
        credit_vc=signed,
    )


def _device_binding_vc(
    agent_did: str,
    binding_level: str,
    country: str,
    asn: int,
    issuer: str,
    private_key_pem: str,
) -> dict:
    from agent_score_engine import sign_credit_vc_jws

    now = datetime.now(timezone.utc) - timedelta(days=1)
    payload = {
        "@context": ["https://www.w3.org/ns/credentials/v2", "https://agent-score.org/v1"],
        "type": ["VerifiableCredential", "AgentDeviceBindingCredential"],
        "issuer": issuer,
        "issuanceDate": now.isoformat().replace("+00:00", "Z"),
        "expirationDate": (now + timedelta(days=30)).isoformat().replace("+00:00", "Z"),
        "credentialSubject": {
            "id": agent_did,
            "binding_level": binding_level,
            "registered_country_code": country,
            "registered_asn": asn,
            "device_attestation": {
                "attestation_type": "tee_sgx_ecdsa_qe3",
                "device_pubkey_hash": "0xabc",
                "agent_did": agent_did,
                "timestamp": int(now.timestamp()),
                "quote": "fake-quote",
                "signature": "fake-sig",
            },
        },
    }
    return sign_credit_vc_jws(payload, issuer=issuer, private_key_pem=private_key_pem)


if __name__ == "__main__":
    unittest.main()
