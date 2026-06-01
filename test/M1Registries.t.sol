// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {IdentityRegistry} from "../src/registries/IdentityRegistry.sol";
import {CreditAuthorityRegistry} from "../src/registries/CreditAuthorityRegistry.sol";
import {ReputationRegistry} from "../src/registries/ReputationRegistry.sol";
import {StakeRegistry} from "../src/registries/StakeRegistry.sol";
import {ValidationRegistry} from "../src/registries/ValidationRegistry.sol";
import {ViolationRegistry} from "../src/registries/ViolationRegistry.sol";

contract MockERC20 {
    string public constant name = "Mock USDC";
    string public constant symbol = "mUSDC";
    uint8 public constant decimals = 6;

    mapping(address account => uint256 balance) public balanceOf;
    mapping(address owner => mapping(address spender => uint256 amount)) public allowance;

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        require(balanceOf[msg.sender] >= amount, "insufficient balance");
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(balanceOf[from] >= amount, "insufficient balance");
        require(allowance[from][msg.sender] >= amount, "insufficient allowance");
        allowance[from][msg.sender] -= amount;
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }
}

contract M1RegistriesTest {
    IdentityRegistry private identity;
    CreditAuthorityRegistry private authorities;
    ReputationRegistry private reputation;
    StakeRegistry private stakes;
    ValidationRegistry private validations;
    ViolationRegistry private violations;
    MockERC20 private token;

    function setUp() public {
        identity = new IdentityRegistry();
        authorities = new CreditAuthorityRegistry(address(this));
        reputation = new ReputationRegistry(identity);
        stakes = new StakeRegistry(address(this), identity);
        validations = new ValidationRegistry(identity);
        violations = new ViolationRegistry(address(this));
        token = new MockERC20();
    }

    function testRegisterAgentAndResolveDID() public {
        setUp();

        uint256 agentId = identity.registerAgent(
            address(this),
            "did:ethr:0x2105:0x0000000000000000000000000000000000008004",
            "did:web:acme.example",
            "ipfs://agent-card"
        );

        require(agentId == 1, "agent id");
        require(identity.ownerOf(agentId) == address(this), "owner");
        require(identity.balanceOf(address(this)) == 1, "balance");
        require(identity.supportsInterface(0x01ffc9a7), "erc165");
        require(identity.supportsInterface(0x80ac58cd), "erc721");
        require(identity.supportsInterface(0x5b5e139f), "erc721 metadata");
        require(identity.getApproved(agentId) == address(0), "approval");
        require(!identity.isApprovedForAll(address(this), address(0xBEEF)), "operator");
        require(
            _eq(identity.didOf(agentId), "did:ethr:0x2105:0x0000000000000000000000000000000000008004"),
            "did"
        );
        require(_eq(identity.principalOf(agentId), "did:web:acme.example"), "principal");
        require(_eq(identity.tokenURI(agentId), "ipfs://agent-card"), "uri");
    }

    function testCreditAuthorityWhitelistLifecycle() public {
        setUp();

        authorities.addAuthority(address(0xCA), "ipfs://authority");
        require(authorities.isAuthority(address(0xCA)), "authority enabled");
        require(_eq(authorities.metadataURIOf(address(0xCA)), "ipfs://authority"), "metadata");

        authorities.removeAuthority(address(0xCA), bytes32("rotate-key"));
        require(!authorities.isAuthority(address(0xCA)), "authority disabled");
    }

    function testStakeERC20AndSlash() public {
        setUp();

        uint256 agentId = identity.registerAgent(
            address(this),
            "did:ethr:0x2105:0x0000000000000000000000000000000000008004",
            "did:web:acme.example",
            "ipfs://agent-card"
        );

        token.mint(address(this), 1_000_000_000);
        token.approve(address(stakes), 1_000_000_000);
        stakes.stake(agentId, address(token), 1_000_000_000, uint64(block.timestamp + 30 days));

        (uint256 amount, uint64 lockUntil) = stakes.positionOf(agentId, address(token));
        require(amount == 1_000_000_000, "stake amount");
        require(lockUntil > block.timestamp, "lock");

        stakes.slash(agentId, address(token), 5_000, address(0xBEEF), bytes32("major-violation"));
        (uint256 remaining,) = stakes.positionOf(agentId, address(token));
        require(remaining == 500_000_000, "remaining stake");
        require(token.balanceOf(address(0xBEEF)) == 500_000_000, "recipient balance");
    }

    function testSubmitReputationAndValidationAnchors() public {
        setUp();

        uint256 agentId = identity.registerAgent(
            address(this),
            "did:ethr:0x2105:0x0000000000000000000000000000000000008004",
            "did:web:acme.example",
            "ipfs://agent-card"
        );

        bytes32 iprRoot = keccak256("ipr-merkle-root");
        reputation.submitIPR(
            agentId,
            iprRoot,
            keccak256("caller-signature"),
            keccak256("callee-signature"),
            "ipfs://ipr-batch"
        );

        require(reputation.iprCountOf(agentId) == 1, "ipr count");
        require(reputation.isSubmittedRoot(iprRoot), "ipr root");

        bytes32 attestationHash = keccak256("tee-attestation");
        validations.submitValidation(agentId, "tee", attestationHash, "ipfs://tee-attestation");

        require(validations.validationCountOf(agentId) == 1, "validation count");
        require(validations.isSubmittedAttestation(attestationHash), "attestation");
    }

    function testRecordPrincipalViolation() public {
        setUp();

        uint256 violationId =
            violations.recordViolation("did:web:acme.example", 80, "ipfs://critical-evidence");
        ViolationRegistry.Violation memory violation = violations.violationAt(violationId);

        bytes32 principalHash = keccak256(bytes("did:web:acme.example"));
        require(violation.principalDIDHash == principalHash, "principal hash");
        require(violation.severity == 80, "severity");
        require(violations.violationCountOf(principalHash) == 1, "violation count");
        require(_eq(violation.evidenceURI, "ipfs://critical-evidence"), "evidence");
    }

    function _eq(string memory a, string memory b) private pure returns (bool) {
        return keccak256(bytes(a)) == keccak256(bytes(b));
    }
}
