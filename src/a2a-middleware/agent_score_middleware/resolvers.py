from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Protocol, Set


class DIDKeyResolver(Protocol):
    def public_key_for(self, did: str) -> Optional[str]:
        """Return the current assertion/authentication public key for a DID."""


@dataclass
class StaticDIDKeyResolver:
    public_key_by_did: Dict[str, str] = field(default_factory=dict)

    def public_key_for(self, did: str) -> Optional[str]:
        return self.public_key_by_did.get(did)


class CredentialStatusResolver(Protocol):
    def is_revoked(self, status_id: str) -> bool:
        """Return true when a credential status entry is revoked."""


@dataclass
class InMemoryCredentialStatusResolver:
    revoked_status_ids: Set[str] = field(default_factory=set)

    def is_revoked(self, status_id: str) -> bool:
        return status_id in self.revoked_status_ids


class TrustRegistryReader(Protocol):
    def is_known_agent(self, agent_did: str) -> bool:
        """Return true when the agent identity is registered."""

    def is_trusted_credit_authority(self, issuer_did: str) -> bool:
        """Return true when the issuer is an active credit authority."""

    def is_trusted_device_authority(self, issuer_did: str) -> bool:
        """Return true when the issuer can issue device attestations."""


@dataclass
class InMemoryTrustRegistry:
    agents: Set[str] = field(default_factory=set)
    credit_authorities: Set[str] = field(default_factory=set)
    device_authorities: Set[str] = field(default_factory=set)

    def is_known_agent(self, agent_did: str) -> bool:
        return agent_did in self.agents

    def is_trusted_credit_authority(self, issuer_did: str) -> bool:
        return issuer_did in self.credit_authorities

    def is_trusted_device_authority(self, issuer_did: str) -> bool:
        return issuer_did in self.device_authorities
