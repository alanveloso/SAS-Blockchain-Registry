// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SASSharedRegistry
 * @dev Smart contract para registro SAS seguindo padrão WinnForum
 * Implementa interface SAS-SAS compatível com WINNF-16-S-0096
 */
contract SASSharedRegistry {
    address public owner;
    mapping(address => bool) public authorizedSAS;

    // Estrutura CBSD seguindo padrão WinnForum
    struct CBSD {
        string fccId;
        string userId;
        string cbsdSerialNumber;
        string callSign;
        string cbsdCategory;
        string airInterface;
        string[] measCapability;
        uint256 eirpCapability;
        int256 latitude;
        int256 longitude;
        uint256 height;
        string heightType;
        bool indoorDeployment;
        uint256 antennaGain;
        uint256 antennaBeamwidth;
        uint256 antennaAzimuth;
        string groupingParam;
        string cbsdAddress;
        address sasOrigin;
        uint256 registrationTimestamp;
    }

    struct Grant {
        string grantId;
        string channelType;
        uint256 grantExpireTime;
        bool terminated;
        uint256 maxEirp;
        uint256 lowFrequency;
        uint256 highFrequency;
        uint256 requestedMaxEirp;
        uint256 requestedLowFrequency;
        uint256 requestedHighFrequency;
        address sasOrigin;
        uint256 grantTimestamp;
    }

    struct RegistrationRequest {
        string fccId;
        string userId;
        string cbsdSerialNumber;
        string callSign;
        string cbsdCategory;
        string airInterface;
        string[] measCapability;
        uint256 eirpCapability;
        int256 latitude;
        int256 longitude;
        uint256 height;
        string heightType;
        bool indoorDeployment;
        uint256 antennaGain;
        uint256 antennaBeamwidth;
        uint256 antennaAzimuth;
        string groupingParam;
        string cbsdAddress;
    }
    struct GrantRequest {
        string fccId;
        string cbsdSerialNumber;
        string channelType;
        uint256 maxEirp;
        uint256 lowFrequency;
        uint256 highFrequency;
        uint256 requestedMaxEirp;
        uint256 requestedLowFrequency;
        uint256 requestedHighFrequency;
        uint256 grantExpireTime;
    }

    mapping(bytes32 => CBSD) public cbsds;
    mapping(bytes32 => Grant[]) public grants;
    uint256 public totalCbsds;
    uint256 public totalGrants;

    event SASAuthorized(address indexed sas);
    event SASRevoked(address indexed sas);
    event CBSDRegistered(string indexed fccId, string indexed serialNumber, address indexed sasOrigin);
    event GrantCreated(string indexed fccId, string indexed serialNumber, string grantId, address indexed sasOrigin);
    event GrantTerminated(string indexed fccId, string indexed serialNumber, string grantId, address indexed sasOrigin);

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

    function _generateCBSDKey(string memory fccId, string memory serialNumber) private pure returns (bytes32) {
        return keccak256(abi.encodePacked(fccId, serialNumber));
    }

    function registration(RegistrationRequest calldata req) external onlyAuthorizedSAS {
        bytes32 cbsdKey = _generateCBSDKey(req.fccId, req.cbsdSerialNumber);
        require(bytes(cbsds[cbsdKey].fccId).length == 0, "CBSD already exists");
        CBSD storage newCbsd = cbsds[cbsdKey];
        newCbsd.fccId = req.fccId;
        newCbsd.userId = req.userId;
        newCbsd.cbsdSerialNumber = req.cbsdSerialNumber;
        newCbsd.callSign = req.callSign;
        newCbsd.cbsdCategory = req.cbsdCategory;
        newCbsd.airInterface = req.airInterface;
        newCbsd.measCapability = req.measCapability;
        newCbsd.eirpCapability = req.eirpCapability;
        newCbsd.latitude = req.latitude;
        newCbsd.longitude = req.longitude;
        newCbsd.height = req.height;
        newCbsd.heightType = req.heightType;
        newCbsd.indoorDeployment = req.indoorDeployment;
        newCbsd.antennaGain = req.antennaGain;
        newCbsd.antennaBeamwidth = req.antennaBeamwidth;
        newCbsd.antennaAzimuth = req.antennaAzimuth;
        newCbsd.groupingParam = req.groupingParam;
        newCbsd.cbsdAddress = req.cbsdAddress;
        newCbsd.sasOrigin = msg.sender;
        newCbsd.registrationTimestamp = block.timestamp;
        totalCbsds++;
        emit CBSDRegistered(req.fccId, req.cbsdSerialNumber, msg.sender);
    }

    function grant(GrantRequest calldata req) external onlyAuthorizedSAS {
        bytes32 cbsdKey = _generateCBSDKey(req.fccId, req.cbsdSerialNumber);
        require(bytes(cbsds[cbsdKey].fccId).length != 0, "CBSD not registered");
        string memory grantId = string(abi.encodePacked("grant_", req.fccId, req.cbsdSerialNumber, grants[cbsdKey].length));
        grants[cbsdKey].push();
        Grant storage newGrant = grants[cbsdKey][grants[cbsdKey].length - 1];
        newGrant.grantId = grantId;
        newGrant.channelType = req.channelType;
        newGrant.grantExpireTime = req.grantExpireTime;
        newGrant.terminated = false;
        newGrant.maxEirp = req.maxEirp;
        newGrant.lowFrequency = req.lowFrequency;
        newGrant.highFrequency = req.highFrequency;
        newGrant.requestedMaxEirp = req.requestedMaxEirp;
        newGrant.requestedLowFrequency = req.requestedLowFrequency;
        newGrant.requestedHighFrequency = req.requestedHighFrequency;
        newGrant.sasOrigin = msg.sender;
        newGrant.grantTimestamp = block.timestamp;
        totalGrants++;
        emit GrantCreated(req.fccId, req.cbsdSerialNumber, grantId, msg.sender);
    }

    function relinquishment(string memory fccId, string memory cbsdSerialNumber, string memory grantId) external onlyAuthorizedSAS {
        bytes32 cbsdKey = _generateCBSDKey(fccId, cbsdSerialNumber);
        require(bytes(cbsds[cbsdKey].fccId).length != 0, "CBSD not registered");
        Grant[] storage grantArray = grants[cbsdKey];
        for (uint i = 0; i < grantArray.length; i++) {
            if (keccak256(bytes(grantArray[i].grantId)) == keccak256(bytes(grantId))) {
                grantArray[i].terminated = true;
                emit GrantTerminated(fccId, cbsdSerialNumber, grantId, msg.sender);
                break;
            }
        }
    }

    function deregistration(string memory fccId, string memory cbsdSerialNumber) external onlyAuthorizedSAS {
        bytes32 cbsdKey = _generateCBSDKey(fccId, cbsdSerialNumber);
        require(bytes(cbsds[cbsdKey].fccId).length != 0, "CBSD not registered");
        delete cbsds[cbsdKey];
        delete grants[cbsdKey];
        totalCbsds--;
    }
} 