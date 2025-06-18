// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CBSDRegistry {

    struct CBSD {
        uint256 id;
        address cbsdAddress;
        uint256 grantAmount;
        string status;
    }

    mapping(uint256 => CBSD) public cbsds;

    event CBSDRegistered(uint256 indexed cbsdId, address indexed cbsdAddress, uint256 grantAmount);

    function registerCBSD(uint256 _id, address _cbsdAddress, uint256 _grantAmount) public {
        cbsds[_id] = CBSD(_id, _cbsdAddress, _grantAmount, "registered");
        emit CBSDRegistered(_id, _cbsdAddress, _grantAmount);
    }

    function updateGrantAmount(uint256 _id, uint256 _newGrantAmount) public {
        require(cbsds[_id].id != 0, "CBSD not registered.");
        cbsds[_id].grantAmount = _newGrantAmount;
        emit CBSDRegistered(_id, cbsds[_id].cbsdAddress, _newGrantAmount);
    }

    function getCBSDInfo(uint256 _id) public view returns (address, uint256, string memory) {
        CBSD memory cbsd = cbsds[_id];
        return (cbsd.cbsdAddress, cbsd.grantAmount, cbsd.status);
    }
}

