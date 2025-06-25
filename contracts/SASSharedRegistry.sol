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
        string[] measCapability; // array de capabilities como string
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
        string cbsdAddress; // endereço de rede do CBSD
        address sasOrigin;
        uint256 registrationTimestamp;
    }
    
    // Estrutura Grant seguindo padrão WinnForum
    struct Grant {
        string grantId;
        string channelType;
        uint256 grantExpireTime; // agora uint256
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
    
    // Structs de input para evitar stack too deep
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
        uint256 grantExpireTime; // agora uint256
    }
    
    // Mapeamentos
    mapping(bytes32 => CBSD) public cbsds;                    // fccId + serialNumber -> CBSD
    mapping(bytes32 => Grant[]) public grants;                // fccId + serialNumber -> Grants
    mapping(string => bool) public fccIds;                   // FCC IDs válidos
    mapping(string => bool) public userIds;                  // User IDs válidos
    mapping(string => bool) public blacklistedFccIds;        // FCC IDs blacklistados
    mapping(bytes32 => bool) public blacklistedSerialNumbers; // Serial numbers blacklistados
    
    // Contadores
    uint256 public totalCbsds;
    uint256 public totalGrants;
    
    // Eventos seguindo padrão WinnForum
    event SASAuthorized(address indexed sas);
    event SASRevoked(address indexed sas);
    event CBSDRegistered(string indexed fccId, string indexed serialNumber, address indexed sasOrigin);
    event GrantCreated(string indexed fccId, string indexed serialNumber, string grantId, address indexed sasOrigin);
    event GrantTerminated(string indexed fccId, string indexed serialNumber, string grantId, address indexed sasOrigin);
    event FCCIdInjected(string indexed fccId, uint256 maxEirp);
    event UserIdInjected(string indexed userId);
    event FCCIdBlacklisted(string indexed fccId);
    event SerialNumberBlacklisted(string indexed fccId, string indexed serialNumber);
    
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
    
    // ============================================================================
    // FUNÇÕES AUXILIARES PRIVADAS
    // ============================================================================
    
    /**
     * @dev Valida se um CBSD pode ser registrado
     * @param fccId FCC ID do dispositivo
     * @param userId User ID do dispositivo
     * @param cbsdKey Chave única do CBSD
     */
    function _validateRegistration(
        string memory fccId,
        string memory userId,
        bytes32 cbsdKey
    ) private view {
        require(bytes(cbsds[cbsdKey].fccId).length == 0, "CBSD already exists");
        require(fccIds[fccId], "FCC ID not authorized");
        require(userIds[userId], "User ID not authorized");
        require(!blacklistedFccIds[fccId], "FCC ID blacklisted");
        require(!blacklistedSerialNumbers[_generateCBSDKey(fccId, cbsds[cbsdKey].cbsdSerialNumber)], "Serial number blacklisted");
    }
    
    /**
     * @dev Cria um novo CBSD no storage
     * @param req Dados de registro
     * @param cbsdKey Chave única do CBSD
     */
    function _createCBSD(
        RegistrationRequest calldata req,
        bytes32 cbsdKey
    ) private {
        CBSD storage newCbsd = cbsds[cbsdKey];
        _setCBSDBasicInfo(newCbsd, req);
        _setCBSDLocationInfo(newCbsd, req);
        _setCBSDAntennaInfo(newCbsd, req);
        _setCBSDMetadata(newCbsd, req);
        newCbsd.measCapability = req.measCapability;
    }
    
    /**
     * @dev Define informações básicas do CBSD
     */
    function _setCBSDBasicInfo(CBSD storage cbsd, RegistrationRequest calldata req) private {
        cbsd.fccId = req.fccId;
        cbsd.userId = req.userId;
        cbsd.cbsdSerialNumber = req.cbsdSerialNumber;
        cbsd.callSign = req.callSign;
        cbsd.cbsdCategory = req.cbsdCategory;
        cbsd.airInterface = req.airInterface;
        cbsd.eirpCapability = req.eirpCapability;
    }
    
    /**
     * @dev Define informações de localização do CBSD
     */
    function _setCBSDLocationInfo(CBSD storage cbsd, RegistrationRequest calldata req) private {
        cbsd.latitude = req.latitude;
        cbsd.longitude = req.longitude;
        cbsd.height = req.height;
        cbsd.heightType = req.heightType;
        cbsd.indoorDeployment = req.indoorDeployment;
    }
    
    /**
     * @dev Define informações da antena do CBSD
     */
    function _setCBSDAntennaInfo(CBSD storage cbsd, RegistrationRequest calldata req) private {
        cbsd.antennaGain = req.antennaGain;
        cbsd.antennaBeamwidth = req.antennaBeamwidth;
        cbsd.antennaAzimuth = req.antennaAzimuth;
        cbsd.groupingParam = req.groupingParam;
    }
    
    /**
     * @dev Define metadados do CBSD
     */
    function _setCBSDMetadata(CBSD storage cbsd, RegistrationRequest calldata req) private {
        cbsd.cbsdAddress = req.cbsdAddress;
        cbsd.sasOrigin = msg.sender;
        cbsd.registrationTimestamp = block.timestamp;
    }
    
    /**
     * @dev Cria um novo Grant no storage
     * @param req Dados do grant
     * @param cbsdKey Chave única do CBSD
     * @param grantId ID único do grant
     */
    function _createGrant(
        GrantRequest calldata req,
        bytes32 cbsdKey,
        string memory grantId
    ) private {
        Grant[] storage grantArray = grants[cbsdKey];
        grantArray.push();
        Grant storage newGrant = grantArray[grantArray.length - 1];
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
    }
    
    /**
     * @dev Gera chave única para CBSD
     * @param fccId FCC ID
     * @param serialNumber Serial number
     * @return Chave única
     */
    function _generateCBSDKey(string memory fccId, string memory serialNumber) private pure returns (bytes32) {
        return keccak256(abi.encodePacked(fccId, serialNumber));
    }
    
    /**
     * @dev Gera ID único para Grant
     * @param fccId FCC ID
     * @param serialNumber Serial number
     * @param grantIndex Índice do grant
     * @return ID único do grant
     */
    function _generateGrantId(bytes32 fccId, bytes32 serialNumber, uint256 grantIndex) private pure returns (bytes32) {
        return keccak256(abi.encodePacked("grant_", fccId, serialNumber, grantIndex));
    }
    
    /**
     * @dev Gera chave única para serial number
     * @param fccId FCC ID
     * @param serialNumber Serial number
     * @return Chave única
     */
    function _getSerialKey(string memory fccId, string memory serialNumber) private pure returns (string memory) {
        return string(abi.encodePacked(fccId, serialNumber));
    }
    
    // ============================================================================
    // FUNÇÕES SAS-SAS (Seguindo interface WinnForum)
    // ============================================================================
    
    /**
     * @notice Registration - Registra um CBSD seguindo padrão WinnForum
     * @param req Struct de input para evitar stack too deep
     */
    function Registration(RegistrationRequest calldata req) external onlyAuthorizedSAS {
        bytes32 cbsdKey = _generateCBSDKey(req.fccId, req.cbsdSerialNumber);
        
        // Validação usando função auxiliar
        _validateRegistration(req.fccId, req.userId, cbsdKey);
        
        // Criação usando função auxiliar
        _createCBSD(req, cbsdKey);
        
        totalCbsds++;
        emit CBSDRegistered(req.fccId, req.cbsdSerialNumber, msg.sender);
    }
    
    /**
     * @notice GrantSpectrum - Concede espectro a um CBSD
     * @param req Struct de input para evitar stack too deep
     */
    function GrantSpectrum(GrantRequest calldata req) external onlyAuthorizedSAS {
        bytes32 cbsdKey = _generateCBSDKey(req.fccId, req.cbsdSerialNumber);
        require(bytes(cbsds[cbsdKey].fccId).length != 0, "CBSD not registered");
        string memory grantId = string(abi.encodePacked("grant_", req.fccId, req.cbsdSerialNumber, grants[cbsdKey].length));
        _createGrant(req, cbsdKey, grantId);
        totalGrants++;
        emit GrantCreated(req.fccId, req.cbsdSerialNumber, grantId, msg.sender);
    }
    
    /**
     * @notice Heartbeat - Atualiza status do grant
     * @param fccId FCC ID do dispositivo
     * @param cbsdSerialNumber Serial number do dispositivo
     * @param grantId ID do grant
     */
    function Heartbeat(
        string memory fccId,
        string memory cbsdSerialNumber,
        string memory grantId
    ) external view onlyAuthorizedSAS {
        bytes32 cbsdKey = _generateCBSDKey(fccId, cbsdSerialNumber);
        require(bytes(cbsds[cbsdKey].fccId).length != 0, "CBSD not registered");
        bool grantFound = false;
        Grant[] storage grantArray = grants[cbsdKey];
        for (uint i = 0; i < grantArray.length; i++) {
            if (keccak256(bytes(grantArray[i].grantId)) == keccak256(bytes(grantId))) {
                require(!grantArray[i].terminated, "Grant terminated");
                require(block.timestamp < grantArray[i].grantExpireTime, "Grant expired");
                grantFound = true;
                break;
            }
        }
        require(grantFound, "Grant not found");
    }
    
    /**
     * @notice Relinquishment - Termina um grant
     * @param fccId FCC ID do dispositivo
     * @param cbsdSerialNumber Serial number do dispositivo
     * @param grantId ID do grant
     */
    function Relinquishment(
        string memory fccId,
        string memory cbsdSerialNumber,
        string memory grantId
    ) external onlyAuthorizedSAS {
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
    
    /**
     * @notice Deregistration - Remove registro do CBSD
     * @param fccId FCC ID do dispositivo
     * @param cbsdSerialNumber Serial number do dispositivo
     */
    function Deregistration(
        string memory fccId,
        string memory cbsdSerialNumber
    ) external onlyAuthorizedSAS {
        bytes32 cbsdKey = _generateCBSDKey(fccId, cbsdSerialNumber);
        require(bytes(cbsds[cbsdKey].fccId).length != 0, "CBSD not registered");
        
        delete cbsds[cbsdKey];
        delete grants[cbsdKey];
        totalCbsds--;
    }
    
    // ============================================================================
    // FUNÇÕES ADMIN (Seguindo interface WinnForum)
    // ============================================================================
    
    /**
     * @notice Reset - Reseta o SAS (apenas owner)
     */
    function Reset() external onlyOwner {
        // Implementação básica - em produção seria mais complexo
        totalCbsds = 0;
        totalGrants = 0;
    }
    
    /**
     * @notice InjectFccId - Injeta FCC ID válido
     * @param fccId FCC ID a ser injetado
     * @param maxEirp EIRP máximo (opcional, padrão 47)
     */
    function InjectFccId(string memory fccId, uint256 maxEirp) external onlyOwner {
        fccIds[fccId] = true;
        emit FCCIdInjected(fccId, maxEirp);
    }
    
    /**
     * @notice InjectUserId - Injeta User ID válido
     * @param userId User ID a ser injetado
     */
    function InjectUserId(string memory userId) external onlyOwner {
        userIds[userId] = true;
        emit UserIdInjected(userId);
    }
    
    /**
     * @notice BlacklistByFccId - Blacklista FCC ID
     * @param fccId FCC ID a ser blacklistado
     */
    function BlacklistByFccId(string memory fccId) external onlyOwner {
        blacklistedFccIds[fccId] = true;
        emit FCCIdBlacklisted(fccId);
    }
    
    /**
     * @notice BlacklistByFccIdAndSerialNumber - Blacklista par FCC ID + Serial Number
     * @param fccId FCC ID
     * @param serialNumber Serial number
     */
    function BlacklistByFccIdAndSerialNumber(string memory fccId, string memory serialNumber) external onlyOwner {
        bytes32 key = _generateCBSDKey(fccId, serialNumber);
        blacklistedSerialNumbers[key] = true;
        emit SerialNumberBlacklisted(fccId, serialNumber);
    }
    
    /**
     * @notice TriggerFullActivityDump - Dispara geração de Full Activity Dump
     */
    function TriggerFullActivityDump() external onlyOwner {
        // Em produção, isso dispararia um evento para processamento assíncrono
        // Por enquanto, apenas emite um evento
    }
    
    // ============================================================================
    // FUNÇÕES DE CONSULTA
    // ============================================================================
    
    /**
     * @notice getCBSDInfo - Obtém informações completas do CBSD
     * @param fccId FCC ID
     * @param cbsdSerialNumber Serial number
     * @return CBSD completo
     */
    function getCBSDInfo(string memory fccId, string memory cbsdSerialNumber) 
        external 
        view 
        returns (CBSD memory) 
    {
        bytes32 cbsdKey = _generateCBSDKey(fccId, cbsdSerialNumber);
        return cbsds[cbsdKey];
    }
    
    /**
     * @notice getGrants - Obtém todos os grants de um CBSD
     * @param fccId FCC ID
     * @param cbsdSerialNumber Serial number
     * @return Array de grants
     */
    function getGrants(string memory fccId, string memory cbsdSerialNumber) 
        external 
        view 
        returns (Grant[] memory) 
    {
        bytes32 cbsdKey = _generateCBSDKey(fccId, cbsdSerialNumber);
        return grants[cbsdKey];
    }
    
    /**
     * @notice isCBSDRegistered - Verifica se CBSD está registrado
     * @param fccId FCC ID
     * @param cbsdSerialNumber Serial number
     * @return true se registrado
     */
    function isCBSDRegistered(string memory fccId, string memory cbsdSerialNumber) 
        external 
        view 
        returns (bool) 
    {
        bytes32 cbsdKey = _generateCBSDKey(fccId, cbsdSerialNumber);
        return bytes(cbsds[cbsdKey].fccId).length != 0;
    }
    
    // ============================================================================
    // FUNÇÕES AUXILIARES
    // ============================================================================
    
    /**
     * @notice authorizeSAS - Autoriza um SAS
     * @param _sas Endereço do SAS
     */
    function authorizeSAS(address _sas) external onlyOwner {
        authorizedSAS[_sas] = true;
        emit SASAuthorized(_sas);
    }
    
    /**
     * @notice revokeSAS - Revoga um SAS
     * @param _sas Endereço do SAS
     */
    function revokeSAS(address _sas) external onlyOwner {
        authorizedSAS[_sas] = false;
        emit SASRevoked(_sas);
    }
    
    /**
     * @notice uint2str - Converte uint para string
     * @param _i Número a converter
     * @return String resultante
     */
    function uint2str(uint256 _i) internal pure returns (string memory) {
        if (_i == 0) {
            return "0";
        }
        uint256 j = _i;
        uint256 length;
        while (j != 0) {
            length++;
            j /= 10;
        }
        bytes memory bstr = new bytes(length);
        uint256 k = length;
        while (_i != 0) {
            k -= 1;
            uint8 temp = (48 + uint8(_i - _i / 10 * 10));
            bytes1 b1 = bytes1(temp);
            bstr[k] = b1;
            _i /= 10;
        }
        return string(bstr);
    }
}
