// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IAgentIdentityRegistry {
    function balanceOf(address account) external view returns (uint256);
    function ownerOf(uint256 agentId) external view returns (address);
    function tokenURI(uint256 agentId) external view returns (string memory);
    function didOf(uint256 agentId) external view returns (string memory);
    function principalOf(uint256 agentId) external view returns (string memory);
    function exists(uint256 agentId) external view returns (bool);
    function supportsInterface(bytes4 interfaceId) external view returns (bool);
}
