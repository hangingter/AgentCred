// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

library AgentScoreTypes {
    uint16 internal constant BPS_DENOMINATOR = 10_000;
    address internal constant NATIVE_ASSET = address(0);

    struct AgentRecord {
        address owner;
        string did;
        string principalDID;
        string agentURI;
        bool exists;
    }

    struct StakePosition {
        uint256 amount;
        uint64 lockUntil;
    }

    struct Authority {
        bool enabled;
        string metadataURI;
    }
}
