// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {AgentScoreTypes} from "../AgentScoreTypes.sol";
import {Ownable} from "../Ownable.sol";
import {IAgentIdentityRegistry} from "../interfaces/IAgentIdentityRegistry.sol";
import {IERC20} from "../interfaces/IERC20.sol";

contract StakeRegistry is Ownable {
    error AgentNotFound(uint256 agentId);
    error NotAgentOwner(uint256 agentId, address caller);
    error InvalidAmount();
    error InvalidLockUntil();
    error InvalidSlashRatio();
    error NativeValueMismatch(uint256 expected, uint256 actual);
    error TransferFailed();
    error StakeLocked(uint64 lockUntil);
    error InsufficientStake(uint256 requested, uint256 available);
    error ZeroAddress();

    event Staked(uint256 indexed agentId, address indexed asset, uint256 amount, uint64 lockUntil);
    event Unstaked(uint256 indexed agentId, address indexed asset, uint256 amount);
    event Slashed(
        uint256 indexed agentId,
        address indexed principal,
        address indexed asset,
        uint256 amount,
        bytes32 reason
    );

    IAgentIdentityRegistry public immutable identityRegistry;

    mapping(uint256 agentId => mapping(address asset => AgentScoreTypes.StakePosition position))
        private _positions;

    constructor(address initialOwner, IAgentIdentityRegistry identityRegistry_) Ownable(initialOwner) {
        if (address(identityRegistry_) == address(0)) revert ZeroAddress();
        identityRegistry = identityRegistry_;
    }

    receive() external payable {}

    function stake(uint256 agentId, address asset, uint256 amount, uint64 lockUntil)
        external
        payable
        onlyAgentOwner(agentId)
    {
        if (amount == 0) revert InvalidAmount();
        if (lockUntil <= block.timestamp) revert InvalidLockUntil();

        if (asset == AgentScoreTypes.NATIVE_ASSET) {
            if (msg.value != amount) revert NativeValueMismatch(amount, msg.value);
        } else {
            if (msg.value != 0) revert NativeValueMismatch(0, msg.value);
            _safeTransferFrom(asset, msg.sender, address(this), amount);
        }

        AgentScoreTypes.StakePosition storage position = _positions[agentId][asset];
        position.amount += amount;
        if (lockUntil > position.lockUntil) {
            position.lockUntil = lockUntil;
        }

        emit Staked(agentId, asset, amount, position.lockUntil);
    }

    function unstake(uint256 agentId, address asset, uint256 amount)
        external
        onlyAgentOwner(agentId)
    {
        if (amount == 0) revert InvalidAmount();
        AgentScoreTypes.StakePosition storage position = _positions[agentId][asset];
        if (block.timestamp < position.lockUntil) revert StakeLocked(position.lockUntil);
        if (amount > position.amount) revert InsufficientStake(amount, position.amount);

        position.amount -= amount;
        _transferAsset(asset, msg.sender, amount);
        emit Unstaked(agentId, asset, amount);
    }

    function slash(
        uint256 agentId,
        address asset,
        uint16 ratioBps,
        address recipient,
        bytes32 reason
    ) external onlyOwner returns (uint256 slashedAmount) {
        if (recipient == address(0)) revert ZeroAddress();
        if (ratioBps == 0 || ratioBps > AgentScoreTypes.BPS_DENOMINATOR) revert InvalidSlashRatio();

        AgentScoreTypes.StakePosition storage position = _positions[agentId][asset];
        slashedAmount = position.amount * ratioBps / AgentScoreTypes.BPS_DENOMINATOR;
        if (slashedAmount == 0) revert InvalidAmount();

        position.amount -= slashedAmount;
        _transferAsset(asset, recipient, slashedAmount);
        emit Slashed(agentId, identityRegistry.ownerOf(agentId), asset, slashedAmount, reason);
    }

    function positionOf(uint256 agentId, address asset)
        external
        view
        returns (uint256 amount, uint64 lockUntil)
    {
        AgentScoreTypes.StakePosition storage position = _positions[agentId][asset];
        return (position.amount, position.lockUntil);
    }

    modifier onlyAgentOwner(uint256 agentId) {
        if (!identityRegistry.exists(agentId)) revert AgentNotFound(agentId);
        if (identityRegistry.ownerOf(agentId) != msg.sender) revert NotAgentOwner(agentId, msg.sender);
        _;
    }

    function _safeTransferFrom(address token, address from, address to, uint256 amount) private {
        bool ok = IERC20(token).transferFrom(from, to, amount);
        if (!ok) revert TransferFailed();
    }

    function _transferAsset(address asset, address to, uint256 amount) private {
        if (asset == AgentScoreTypes.NATIVE_ASSET) {
            (bool ok,) = to.call{value: amount}("");
            if (!ok) revert TransferFailed();
        } else {
            bool ok = IERC20(asset).transfer(to, amount);
            if (!ok) revert TransferFailed();
        }
    }
}
