// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IdentityRegistry} from "../src/registries/IdentityRegistry.sol";
import {CreditAuthorityRegistry} from "../src/registries/CreditAuthorityRegistry.sol";
import {ReputationRegistry} from "../src/registries/ReputationRegistry.sol";
import {StakeRegistry} from "../src/registries/StakeRegistry.sol";
import {ValidationRegistry} from "../src/registries/ValidationRegistry.sol";
import {ViolationRegistry} from "../src/registries/ViolationRegistry.sol";

contract DeployM1 {
    struct Deployment {
        IdentityRegistry identityRegistry;
        CreditAuthorityRegistry creditAuthorityRegistry;
        ReputationRegistry reputationRegistry;
        StakeRegistry stakeRegistry;
        ValidationRegistry validationRegistry;
        ViolationRegistry violationRegistry;
    }

    function deploy(address admin) external returns (Deployment memory deployment) {
        deployment.identityRegistry = new IdentityRegistry();
        deployment.creditAuthorityRegistry = new CreditAuthorityRegistry(admin);
        deployment.reputationRegistry = new ReputationRegistry(deployment.identityRegistry);
        deployment.stakeRegistry = new StakeRegistry(admin, deployment.identityRegistry);
        deployment.validationRegistry = new ValidationRegistry(deployment.identityRegistry);
        deployment.violationRegistry = new ViolationRegistry(admin);
    }
}
