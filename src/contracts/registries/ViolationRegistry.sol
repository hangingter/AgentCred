// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Ownable} from "../Ownable.sol";

contract ViolationRegistry is Ownable {
    error EmptyPrincipalDID();
    error InvalidSeverity();
    error EmptyEvidenceURI();

    struct Violation {
        bytes32 principalDIDHash;
        uint8 severity;
        uint64 recordedAt;
        string evidenceURI;
    }

    event ViolationRecorded(
        bytes32 indexed principalDIDHash,
        address indexed reporter,
        uint8 severity,
        string evidenceURI
    );

    Violation[] private _violations;
    mapping(bytes32 principalDIDHash => uint256 count) public violationCountOf;

    constructor(address initialOwner) Ownable(initialOwner) {}

    function recordViolation(string calldata principalDID, uint8 severity, string calldata evidenceURI)
        external
        onlyOwner
        returns (uint256 violationId)
    {
        if (bytes(principalDID).length == 0) revert EmptyPrincipalDID();
        if (severity > 100) revert InvalidSeverity();
        if (bytes(evidenceURI).length == 0) revert EmptyEvidenceURI();

        bytes32 principalDIDHash = keccak256(bytes(principalDID));
        violationId = _violations.length;
        _violations.push(
            Violation({
                principalDIDHash: principalDIDHash,
                severity: severity,
                recordedAt: uint64(block.timestamp),
                evidenceURI: evidenceURI
            })
        );
        violationCountOf[principalDIDHash] += 1;

        emit ViolationRecorded(principalDIDHash, msg.sender, severity, evidenceURI);
    }

    function violationAt(uint256 violationId) external view returns (Violation memory) {
        return _violations[violationId];
    }

    function violationCount() external view returns (uint256) {
        return _violations.length;
    }
}
