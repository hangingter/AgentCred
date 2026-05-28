from __future__ import annotations

from typing import Any


INTERACTION_PROOF_RECORD_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["client_id", "success", "on_time"],
    "properties": {
        "client_id": {"type": "string", "minLength": 1},
        "success": {"type": "boolean"},
        "on_time": {"type": "boolean"},
        "caller_signed": {"type": "boolean", "default": True},
        "callee_signed": {"type": "boolean", "default": True},
    },
}

STAKE_SNAPSHOT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["asset", "usd_value"],
    "properties": {
        "asset": {"type": "string", "minLength": 1},
        "usd_value": {"type": "number", "minimum": 0},
        "weight": {"type": "number", "minimum": 0, "default": 1.0},
        "lock_days_remaining": {"type": "integer", "minimum": 0, "default": 30},
    },
}

VIOLATION_EVENT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["severity", "days_ago"],
    "properties": {
        "severity": {"type": "integer", "minimum": 0, "maximum": 100},
        "days_ago": {"type": "integer", "minimum": 0},
    },
}

CREDIT_VC_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": True,
    "required": ["@context", "type", "issuer", "validFrom", "validUntil", "credentialSubject"],
    "properties": {
        "@context": {"type": "array", "items": {"type": "string"}},
        "type": {"type": "array", "items": {"type": "string"}},
        "issuer": {"type": "string", "minLength": 1},
        "validFrom": {"type": "string", "format": "date-time"},
        "validUntil": {"type": "string", "format": "date-time"},
        "credentialSubject": {
            "type": "object",
            "required": ["id", "score", "tier", "dimensions", "reason_codes"],
            "properties": {
                "id": {"type": "string", "minLength": 1},
                "score": {"type": "integer", "minimum": 0, "maximum": 1000},
                "tier": {"type": "string", "enum": ["S", "A", "B", "C", "D"]},
                "dimensions": {"type": "object"},
                "violation_penalty": {"type": "number", "minimum": 0},
                "violation_count_90d": {"type": "integer", "minimum": 0},
                "snapshot_root": {"type": ["string", "null"]},
                "reason_codes": {"type": "array", "items": {"type": "string"}},
            },
        },
        "proof": {"type": "object"},
    },
}


def export_json_schemas() -> dict[str, dict[str, Any]]:
    return {
        "InteractionProofRecord": INTERACTION_PROOF_RECORD_SCHEMA,
        "StakeSnapshot": STAKE_SNAPSHOT_SCHEMA,
        "ViolationEvent": VIOLATION_EVENT_SCHEMA,
        "CreditVC": CREDIT_VC_SCHEMA,
    }
