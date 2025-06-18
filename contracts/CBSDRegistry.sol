// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CBSDRegistry {
    address public owner;

    struct CBSD {
        uint256 id;
        address cbsdAddress;
        uint256 grantAmount;
        string status;
    }

    mapping(uint256 => CBSD) public cbsds;

    event CBSDRegistered(uint256 indexed cbsdId, address indexed cbsdAddress, uint256 grantAmount);
    event GrantAmountUpdated(uint256 indexed cbsdId, uint256 newGrantAmount);
    event StatusUpdated(uint256 indexed cbsdId, string newStatus);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function registerCBSD(uint256 _id, address _cbsdAddress, uint256 _grantAmount) public onlyOwner {
        require(cbsds[_id].id == 0, "CBSD already registered.");
        cbsds[_id] = CBSD(_id, _cbsdAddress, _grantAmount, "registered");
        emit CBSDRegistered(_id, _cbsdAddress, _grantAmount);
    }

    function updateGrantAmount(uint256 _id, uint256 _newGrantAmount) public onlyOwner {
        require(cbsds[_id].id != 0, "CBSD not registered.");
        cbsds[_id].grantAmount = _newGrantAmount;
        emit GrantAmountUpdated(_id, _newGrantAmount);
    }

    function updateStatus(uint256 _id, string memory _newStatus) public onlyOwner {
        require(cbsds[_id].id != 0, "CBSD not registered.");
        cbsds[_id].status = _newStatus;
        emit StatusUpdated(_id, _newStatus);
    }

    function getCBSDInfo(uint256 _id) public view returns (address, uint256, string memory) {
        CBSD memory cbsd = cbsds[_id];
        return (cbsd.cbsdAddress, cbsd.grantAmount, cbsd.status);
    }
}

