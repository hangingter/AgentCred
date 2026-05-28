// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IAgentIdentityRegistry {
    function ownerOf(uint256 agentId) external view returns (address);
    function didOf(uint256 agentId) external view returns (string memory);
    function principalOf(uint256 agentId) external view returns (string memory);
    function exists(uint256 agentId) external view returns (bool);
}
