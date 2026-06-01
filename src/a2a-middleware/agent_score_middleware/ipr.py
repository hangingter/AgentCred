from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any, Dict

from agent_score_engine import sign_json_jws, verify_json_jws


def sign_payload(payload: Dict[str, Any], secret: str) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hmac.new(secret.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).hexdigest()


def sha256_json(payload: Dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def sign_payload_jws(payload: Dict[str, Any], signer_did: str, private_key_pem: str) -> str:
    if not signer_did:
        raise ValueError("signer_did is required")
    return sign_json_jws(_canonical_payload(payload), private_key_pem, kid=signer_did)


def verify_payload_jws(payload: Dict[str, Any], signature: str, signer_did: str, public_key_pem: str) -> bool:
    verified = verify_json_jws(signature, public_key_pem, expected_alg="ES256K", expected_kid=signer_did)
    return verified == _canonical_payload(payload)


def _canonical_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    return json.loads(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True))
