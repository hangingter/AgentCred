from __future__ import annotations

import base64
import json
from typing import Any, Dict

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, utils


def generate_es256k_private_key_pem() -> str:
    private_key = ec.generate_private_key(ec.SECP256K1())
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("ascii")


def public_key_pem_from_private_key(private_key_pem: str) -> str:
    private_key = _load_private_key(private_key_pem)
    return private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")


def sign_json_jws(payload: Dict[str, Any], private_key_pem: str, kid: str) -> str:
    header = {"alg": "ES256K", "typ": "JWT", "kid": kid}
    signing_input = (
        _b64url_json(header) + "." + _b64url_json(payload)
    ).encode("ascii")
    private_key = _load_private_key(private_key_pem)
    der_signature = private_key.sign(signing_input, ec.ECDSA(hashes.SHA256()))
    r, s = utils.decode_dss_signature(der_signature)
    raw_signature = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    return signing_input.decode("ascii") + "." + _b64url(raw_signature)


def verify_json_jws(
    jws: str,
    public_key_pem: str,
    expected_alg: str | None = "ES256K",
    expected_kid: str | None = None,
) -> Dict[str, Any] | None:
    parts = jws.split(".")
    if len(parts) != 3:
        return None
    try:
        header = json.loads(_b64url_decode(parts[0]).decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(header, dict):
        return None
    if expected_alg is not None and header.get("alg") != expected_alg:
        return None
    if expected_kid is not None and header.get("kid") != expected_kid:
        return None
    signing_input = (parts[0] + "." + parts[1]).encode("ascii")
    raw_signature = _b64url_decode(parts[2])
    if len(raw_signature) != 64:
        return None
    r = int.from_bytes(raw_signature[:32], "big")
    s = int.from_bytes(raw_signature[32:], "big")
    der_signature = utils.encode_dss_signature(r, s)
    public_key = _load_public_key(public_key_pem)
    try:
        public_key.verify(der_signature, signing_input, ec.ECDSA(hashes.SHA256()))
    except InvalidSignature:
        return None
    payload = json.loads(_b64url_decode(parts[1]).decode("utf-8"))
    return payload if isinstance(payload, dict) else None


def _load_private_key(private_key_pem: str):
    key = serialization.load_pem_private_key(private_key_pem.encode("ascii"), password=None)
    if not isinstance(key, ec.EllipticCurvePrivateKey):
        raise ValueError("private key must be an EC key")
    if not isinstance(key.curve, ec.SECP256K1):
        raise ValueError("private key must use secp256k1")
    return key


def _load_public_key(public_key_pem: str):
    key = serialization.load_pem_public_key(public_key_pem.encode("ascii"))
    if not isinstance(key, ec.EllipticCurvePublicKey):
        raise ValueError("public key must be an EC key")
    if not isinstance(key.curve, ec.SECP256K1):
        raise ValueError("public key must use secp256k1")
    return key


def _b64url_json(payload: Dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )
    return _b64url(canonical)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)
