// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SASSharedRegistry {
    address public owner;
    mapping(address => bool) public authorizedSAS;

    event SASAuthorized(address indexed sas);
    event SASRevoked(address indexed sas);

    event Registration(address indexed from, string payload, uint256 timestamp);
    event Grant(address indexed from, string payload, uint256 timestamp);
    event Heartbeat(address indexed from, string payload, uint256 timestamp);
    event Relinquishment(address indexed from, string payload, uint256 timestamp);
    event Deregistration(address indexed from, string payload, uint256 timestamp);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    modifier onlyAuthorizedSAS() {
        require(authorizedSAS[msg.sender], "Not an authorized SAS");
        _;
    }

    constructor() {
        owner = msg.sender;
        authorizedSAS[msg.sender] = true;
        emit SASAuthorized(msg.sender);
    }

    function authorizeSAS(address _sas) external onlyOwner {
        authorizedSAS[_sas] = true;
        emit SASAuthorized(_sas);
    }

    function revokeSAS(address _sas) external onlyOwner {
        authorizedSAS[_sas] = false;
        emit SASRevoked(_sas);
    }

    function registration(string calldata payload) external onlyAuthorizedSAS {
        emit Registration(msg.sender, payload, block.timestamp);
    }

    function grant(string calldata payload) external onlyAuthorizedSAS {
        emit Grant(msg.sender, payload, block.timestamp);
    }

    function heartbeat(string calldata payload) external onlyAuthorizedSAS {
        emit Heartbeat(msg.sender, payload, block.timestamp);
    }

    function relinquishment(string calldata payload) external onlyAuthorizedSAS {
        emit Relinquishment(msg.sender, payload, block.timestamp);
    }

    function deregistration(string calldata payload) external onlyAuthorizedSAS {
        emit Deregistration(msg.sender, payload, block.timestamp);
    }
} 