// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AgentScoreTypes} from "../AgentScoreTypes.sol";

contract IdentityRegistry {
    error AgentNotFound(uint256 agentId);
    error NotAgentOwner(uint256 agentId, address caller);
    error SoulboundToken();
    error EmptyDID();
    error EmptyPrincipalDID();
    error DIDAlreadyRegistered(bytes32 didHash);
    error ZeroAddress();

    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);
    event AgentRegistered(
        uint256 indexed agentId,
        address indexed owner,
        string did,
        string principalDID,
        string agentURI
    );
    event AgentURIUpdated(uint256 indexed agentId, string agentURI);
    event PrincipalUpdated(uint256 indexed agentId, string principalDID);

    string public constant name = "Agent-Score Identity";
    string public constant symbol = "ASID";

    uint256 public nextAgentId = 1;

    mapping(uint256 agentId => AgentScoreTypes.AgentRecord record) private _records;
    mapping(address owner => uint256 balance) private _balances;
    mapping(bytes32 didHash => uint256 agentId) public agentIdByDIDHash;

    function registerAgent(
        address agentOwner,
        string calldata did,
        string calldata principalDID,
        string calldata agentURI
    ) external returns (uint256 agentId) {
        if (agentOwner == address(0)) revert ZeroAddress();
        if (bytes(did).length == 0) revert EmptyDID();
        if (bytes(principalDID).length == 0) revert EmptyPrincipalDID();

        bytes32 didHash = keccak256(bytes(did));
        if (agentIdByDIDHash[didHash] != 0) revert DIDAlreadyRegistered(didHash);

        agentId = nextAgentId++;
        _records[agentId] = AgentScoreTypes.AgentRecord({
            owner: agentOwner,
            did: did,
            principalDID: principalDID,
            agentURI: agentURI,
            exists: true
        });
        _balances[agentOwner] += 1;
        agentIdByDIDHash[didHash] = agentId;

        emit Transfer(address(0), agentOwner, agentId);
        emit AgentRegistered(agentId, agentOwner, did, principalDID, agentURI);
    }

    function setAgentURI(uint256 agentId, string calldata agentURI) external onlyAgentOwner(agentId) {
        _records[agentId].agentURI = agentURI;
        emit AgentURIUpdated(agentId, agentURI);
    }

    function setPrincipalDID(uint256 agentId, string calldata principalDID)
        external
        onlyAgentOwner(agentId)
    {
        if (bytes(principalDID).length == 0) revert EmptyPrincipalDID();
        _records[agentId].principalDID = principalDID;
        emit PrincipalUpdated(agentId, principalDID);
    }

    function balanceOf(address account) external view returns (uint256) {
        if (account == address(0)) revert ZeroAddress();
        return _balances[account];
    }

    function ownerOf(uint256 agentId) public view returns (address) {
        AgentScoreTypes.AgentRecord storage record = _recordOf(agentId);
        return record.owner;
    }

    function didOf(uint256 agentId) external view returns (string memory) {
        return _recordOf(agentId).did;
    }

    function principalOf(uint256 agentId) external view returns (string memory) {
        return _recordOf(agentId).principalDID;
    }

    function tokenURI(uint256 agentId) external view returns (string memory) {
        return _recordOf(agentId).agentURI;
    }

    function exists(uint256 agentId) external view returns (bool) {
        return _records[agentId].exists;
    }

    function transferFrom(address, address, uint256) external pure {
        revert SoulboundToken();
    }

    function safeTransferFrom(address, address, uint256) external pure {
        revert SoulboundToken();
    }

    function safeTransferFrom(address, address, uint256, bytes calldata) external pure {
        revert SoulboundToken();
    }

    modifier onlyAgentOwner(uint256 agentId) {
        if (!_records[agentId].exists) revert AgentNotFound(agentId);
        if (_records[agentId].owner != msg.sender) revert NotAgentOwner(agentId, msg.sender);
        _;
    }

    function _recordOf(uint256 agentId)
        private
        view
        returns (AgentScoreTypes.AgentRecord storage record)
    {
        record = _records[agentId];
        if (!record.exists) revert AgentNotFound(agentId);
    }
}
