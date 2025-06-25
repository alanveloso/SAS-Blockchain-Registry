const { ethers } = require('ethers');
const { TestHelper } = require('./nonce-manager.js');

async function testWithHelper() {
    // Conectar ao provider
    const provider = new ethers.JsonRpcProvider('http://127.0.0.1:8545');
    
    // Criar wallet com a chave privada do owner
    const privateKey = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80';
    const wallet = new ethers.Wallet(privateKey, provider);
    
    // Endereço do contrato
    const contractAddress = '0x5FbDB2315678afecb367f032d93F642f64180aa3';
    
    // ABI completo
    const abi = [
        "function owner() external view returns (address)",
        "function totalCbsds() external view returns (uint256)",
        "function totalGrants() external view returns (uint256)",
        "function authorizedSAS(address) external view returns (bool)",
        "function InjectFccId(bytes32 fccId, uint256 maxEirp) external",
        "function InjectUserId(bytes32 userId) external",
        "function Registration(tuple(bytes32 fccId, bytes32 userId, bytes32 cbsdSerialNumber, bytes32 callSign, bytes32 cbsdCategory, bytes32 airInterface, bytes32[] measCapability, uint256 eirpCapability, uint256 latitude, uint256 longitude, uint256 height, bytes32 heightType, bool indoorDeployment, uint256 antennaGain, uint256 antennaBeamwidth, uint256 antennaAzimuth, bytes32 groupingParam, address cbsdAddress)) external",
        "function GrantSpectrum(tuple(bytes32 fccId, bytes32 cbsdSerialNumber, bytes32 channelType, uint256 maxEirp, uint256 lowFrequency, uint256 highFrequency, uint256 requestedMaxEirp, uint256 requestedLowFrequency, uint256 requestedHighFrequency, uint256 grantExpireTime)) external",
        "function Heartbeat(bytes32 fccId, bytes32 cbsdSerialNumber, bytes32 grantId) external view",
        "function Relinquishment(bytes32 fccId, bytes32 cbsdSerialNumber, bytes32 grantId) external",
        "function Deregistration(bytes32 fccId, bytes32 cbsdSerialNumber) external",
        "function BlacklistByFccId(bytes32 fccId) external",
        "function BlacklistByFccIdAndSerialNumber(bytes32 fccId, bytes32 serialNumber) external",
        "function authorizeSAS(address _sas) external",
        "function revokeSAS(address _sas) external",
        "function isCBSDRegistered(bytes32 fccId, bytes32 cbsdSerialNumber) external view returns (bool)",
        "function getCBSDInfo(bytes32 fccId, bytes32 cbsdSerialNumber) external view returns (tuple(bytes32 fccId, bytes32 userId, bytes32 cbsdSerialNumber, bytes32 callSign, bytes32 cbsdCategory, bytes32 airInterface, bytes32[] measCapability, uint256 eirpCapability, uint256 latitude, uint256 longitude, uint256 height, bytes32 heightType, bool indoorDeployment, uint256 antennaGain, uint256 antennaBeamwidth, uint256 antennaAzimuth, bytes32 groupingParam, address cbsdAddress, address sasOrigin, uint256 registrationTimestamp))",
        "function getGrants(bytes32 fccId, bytes32 cbsdSerialNumber) external view returns (tuple(bytes32 grantId, bytes32 channelType, uint256 grantExpireTime, bool terminated, uint256 maxEirp, uint256 lowFrequency, uint256 highFrequency, uint256 requestedMaxEirp, uint256 requestedLowFrequency, uint256 requestedHighFrequency, address sasOrigin, uint256 grantTimestamp)[])"
    ];
    
    try {
        // Criar helper com gerenciador de nonce
        const helper = new TestHelper(provider, wallet, contractAddress, abi);
        
        // Executar teste completo
        await helper.runFullSASFlow();
        
        console.log('\n🎯 TESTE COM HELPER CONCLUÍDO COM SUCESSO!');
        console.log('✅ Gerenciador de nonce funcionando perfeitamente');
        console.log('✅ Todas as funções testadas sem problemas de nonce');
        console.log('✅ Sistema pronto para produção');
        
    } catch (error) {
        console.error('❌ Erro no teste com helper:', error.message);
        console.error('Stack:', error.stack);
    }
}

testWithHelper(); 