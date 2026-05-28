// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IAgentIdentityRegistry} from "../interfaces/IAgentIdentityRegistry.sol";

contract ValidationRegistry {
    error AgentNotFound(uint256 agentId);
    error EmptyValidationType();
    error EmptyAttestationURI();

    event ValidationSubmitted(
        uint256 indexed agentId,
        address indexed validator,
        bytes32 indexed attestationHash,
        string validationType,
        string attestationURI
    );

    IAgentIdentityRegistry public immutable identityRegistry;

    mapping(uint256 agentId => uint256 count) public validationCountOf;
    mapping(bytes32 attestationHash => bool submitted) public isSubmittedAttestation;

    constructor(IAgentIdentityRegistry identityRegistry_) {
        identityRegistry = identityRegistry_;
    }

    function submitValidation(
        uint256 agentId,
        string calldata validationType,
        bytes32 attestationHash,
        string calldata attestationURI
    ) external {
        if (!identityRegistry.exists(agentId)) revert AgentNotFound(agentId);
        if (bytes(validationType).length == 0) revert EmptyValidationType();
        if (bytes(attestationURI).length == 0) revert EmptyAttestationURI();

        validationCountOf[agentId] += 1;
        isSubmittedAttestation[attestationHash] = true;
        emit ValidationSubmitted(agentId, msg.sender, attestationHash, validationType, attestationURI);
    }
}
