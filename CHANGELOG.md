# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-28

### Added
- Initial protocol specification (§1-16) covering identity, credit scoring, handshake, and device binding
- M1: Solidity registry contracts compatible with ERC-8004
  - IdentityRegistry: Agent identity registration with Soulbound ERC-721
  - ReputationRegistry: IPR hash anchoring
  - StakeRegistry: Multi-asset staking with slash mechanism
  - ValidationRegistry: Third-party validation attestation storage
  - ViolationRegistry: Violation records bound to Principal
  - CreditAuthorityRegistry: Whitelist management for credit issuers
- M2: Credit Engine with six-dimensional scoring model
  - BehaviorScore: Historical interaction success and punctuality
  - StakeScore: Economic stake with concentration penalty
  - EndorsementScore: Cross-domain endorsement with PageRank and diversity factor
  - ValidationScore: Third-party validation with type-weighted scoring
  - DeviceScore: Hardware binding level with network drift detection
  - PrincipalScore: Principal credit pass-through
- M3: A2A Middleware with trust handshake layer
  - AgentCard parsing and verification
  - CreditVC integrity, validity, and issuer whitelist checks
  - Configurable policy engine with credit thresholds and device binding requirements
  - Dual-signed IPR generation and hash calculation
  - FastAPI HTTP adapter for quick integration
- M3.3: Device & Network Binding feature
  - Four binding levels: none → registration → runtime → strong
  - TPM/TEE hardware attestation support
  - Network fingerprinting with IP prefix, ASN, and country code
  - Drift detection with Principal co-sign authorization
  - 24-hour short-lived DeviceBindingVC
- JWS ES256K proof with alg/kid header validation to prevent algorithm downgrade attacks
- Dual-signed IPR (Interaction Proof Record) with chain anchoring abstraction
- Demo applications:
  - Minimal demo: Agent identity declaration and two-party trading flow
  - MVP demo: Full protocol simulation with local agents
  - HTTP demo: FastAPI A2A integration example
- Bilingual whitepaper (Chinese/English) with 13 chapters covering architecture, security, and roadmap
- Full test coverage: 37 test cases with 100% pass rate
- Standard Git repository structure with docs, src, demos, and configuration files

### Security
- JWS header validation enforcing `alg=ES256K` and `kid=issuer`
- Device binding preventing key theft across devices
- Network drift detection identifying unauthorized location changes
- Principal association ensuring accountability for violations
- Dual signature mechanism preventing transaction repudiation
