// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AgentScoreTypes} from "../AgentScoreTypes.sol";
import {Ownable} from "../Ownable.sol";

contract CreditAuthorityRegistry is Ownable {
    error AuthorityNotFound(address authority);
    error ZeroAddress();

    event AuthorityAdded(address indexed authority, string metadataURI);
    event AuthorityRemoved(address indexed authority, bytes32 reason);
    event AuthorityMetadataUpdated(address indexed authority, string metadataURI);

    mapping(address authority => AgentScoreTypes.Authority config) private _authorities;

    constructor(address initialOwner) Ownable(initialOwner) {}

    function addAuthority(address authority, string calldata metadataURI) external onlyOwner {
        if (authority == address(0)) revert ZeroAddress();
        _authorities[authority] =
            AgentScoreTypes.Authority({enabled: true, metadataURI: metadataURI});
        emit AuthorityAdded(authority, metadataURI);
    }

    function removeAuthority(address authority, bytes32 reason) external onlyOwner {
        if (!_authorities[authority].enabled) revert AuthorityNotFound(authority);
        _authorities[authority].enabled = false;
        emit AuthorityRemoved(authority, reason);
    }

    function setAuthorityMetadata(address authority, string calldata metadataURI) external onlyOwner {
        if (!_authorities[authority].enabled) revert AuthorityNotFound(authority);
        _authorities[authority].metadataURI = metadataURI;
        emit AuthorityMetadataUpdated(authority, metadataURI);
    }

    function isAuthority(address authority) external view returns (bool) {
        return _authorities[authority].enabled;
    }

    function metadataURIOf(address authority) external view returns (string memory) {
        if (!_authorities[authority].enabled) revert AuthorityNotFound(authority);
        return _authorities[authority].metadataURI;
    }
}
