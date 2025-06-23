// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SASSharedRegistry {
    address public owner;
    mapping(address => bool) public authorizedSAS;

    struct CBSD {
        uint256 id;
        address cbsdAddress;
        uint256 grantAmount;
        string status;
        uint256 frequencyHz;
        uint256 bandwidthHz;
        uint256 expiryTimestamp;
        address sasOrigin;
    }

    mapping(uint256 => CBSD) public cbsds;

    event SASAuthorized(address indexed sas);
    event SASRevoked(address indexed sas);
    event CBSDRegistered(uint256 indexed cbsdId, address indexed sasOrigin);
    event GrantAmountUpdated(uint256 indexed cbsdId, uint256 newGrantAmount, address indexed sasOrigin);
    event StatusUpdated(uint256 indexed cbsdId, string newStatus, address indexed sasOrigin);
    event GrantDetailsUpdated(
        uint256 indexed cbsdId,
        uint256 frequencyHz,
        uint256 bandwidthHz,
        uint256 expiryTimestamp,
        address indexed sasOrigin
    );

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

    /// @notice Permite ao owner autorizar um novo SAS
    function authorizeSAS(address _sas) external onlyOwner {
        authorizedSAS[_sas] = true;
        emit SASAuthorized(_sas);
    }

    /// @notice Permite ao owner revogar um SAS
    function revokeSAS(address _sas) external onlyOwner {
        authorizedSAS[_sas] = false;
        emit SASRevoked(_sas);
    }

    /// @notice Registra um novo CBSD na blockchain
    function registerCBSD(
        uint256 _id,
        address _cbsdAddress,
        uint256 _grantAmount,
        uint256 _frequencyHz,
        uint256 _bandwidthHz,
        uint256 _expiryTimestamp
    ) external onlyAuthorizedSAS {
        require(cbsds[_id].id == 0, "CBSD already exists");
        cbsds[_id] = CBSD(
            _id,
            _cbsdAddress,
            _grantAmount,
            "registered",
            _frequencyHz,
            _bandwidthHz,
            _expiryTimestamp,
            msg.sender
        );
        emit CBSDRegistered(_id, msg.sender);
    }

    /// @notice Atualiza apenas o valor do grant
    function updateGrantAmount(uint256 _id, uint256 _newGrantAmount) external onlyAuthorizedSAS {
        require(cbsds[_id].id != 0, "CBSD not registered");
        CBSD storage c = cbsds[_id];
        c.grantAmount = _newGrantAmount;
        c.sasOrigin = msg.sender;
        emit GrantAmountUpdated(_id, _newGrantAmount, msg.sender);
    }

    /// @notice Atualiza apenas o status do CBSD
    function updateStatus(uint256 _id, string calldata _newStatus) external onlyAuthorizedSAS {
        require(cbsds[_id].id != 0, "CBSD not registered");
        CBSD storage c = cbsds[_id];
        c.status = _newStatus;
        c.sasOrigin = msg.sender;
        emit StatusUpdated(_id, _newStatus, msg.sender);
    }

    /// @notice Atualiza detalhes do grant (frequência, largura de banda e validade)
    function updateGrantDetails(
        uint256 _id,
        uint256 _frequencyHz,
        uint256 _bandwidthHz,
        uint256 _expiryTimestamp
    ) external onlyAuthorizedSAS {
        require(cbsds[_id].id != 0, "CBSD not registered");
        CBSD storage c = cbsds[_id];
        c.frequencyHz = _frequencyHz;
        c.bandwidthHz = _bandwidthHz;
        c.expiryTimestamp = _expiryTimestamp;
        c.sasOrigin = msg.sender;
        emit GrantDetailsUpdated(_id, _frequencyHz, _bandwidthHz, _expiryTimestamp, msg.sender);
    }

    /// @notice Consulta completa de todas as informações de um CBSD
    function getCBSDInfo(uint256 _id)
        external
        view
        returns (
            address cbsdAddress,
            uint256 grantAmount,
            string memory status,
            uint256 frequencyHz,
            uint256 bandwidthHz,
            uint256 expiryTimestamp,
            address sasOrigin
        )
    {
        CBSD memory c = cbsds[_id];
        return (
            c.cbsdAddress,
            c.grantAmount,
            c.status,
            c.frequencyHz,
            c.bandwidthHz,
            c.expiryTimestamp,
            c.sasOrigin
        );
    }

    /// @notice Verifica se o grant ainda está ativo (antes da data de expiração)
    function isActive(uint256 _id) external view returns (bool) {
        CBSD memory c = cbsds[_id];
        return block.timestamp < c.expiryTimestamp;
    }
}
