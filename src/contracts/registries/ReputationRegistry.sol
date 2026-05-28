// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IAgentIdentityRegistry} from "../interfaces/IAgentIdentityRegistry.sol";

contract ReputationRegistry {
    error AgentNotFound(uint256 agentId);
    error EmptyRoot();
    error EmptyEvidenceURI();

    event IPRSubmitted(
        uint256 indexed agentId,
        bytes32 indexed root,
        address indexed submitter,
        bytes32 callerSigHash,
        bytes32 calleeSigHash,
        string evidenceURI
    );

    IAgentIdentityRegistry public immutable identityRegistry;

    mapping(uint256 agentId => uint256 count) public iprCountOf;
    mapping(bytes32 root => bool submitted) public isSubmittedRoot;

    constructor(IAgentIdentityRegistry identityRegistry_) {
        identityRegistry = identityRegistry_;
    }

    function submitIPR(
        uint256 agentId,
        bytes32 root,
        bytes32 callerSigHash,
        bytes32 calleeSigHash,
        string calldata evidenceURI
    ) external {
        if (!identityRegistry.exists(agentId)) revert AgentNotFound(agentId);
        if (root == bytes32(0)) revert EmptyRoot();
        if (bytes(evidenceURI).length == 0) revert EmptyEvidenceURI();

        iprCountOf[agentId] += 1;
        isSubmittedRoot[root] = true;
        emit IPRSubmitted(agentId, root, msg.sender, callerSigHash, calleeSigHash, evidenceURI);
    }
}
