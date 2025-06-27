const { ethers } = require('ethers');

class NonceManager {
    constructor(provider, wallet) {
        this.provider = provider;
        this.wallet = wallet;
        this.currentNonce = null;
    }

    async getNextNonce() {
        if (this.currentNonce === null) {
            this.currentNonce = await this.provider.getTransactionCount(this.wallet.address);
        } else {
            this.currentNonce++;
        }
        return this.currentNonce;
    }

    async waitForTransaction(tx) {
        const receipt = await tx.wait();
        console.log(`  ✅ Transação confirmada no bloco ${receipt.blockNumber}`);
        return receipt;
    }

    async sendTransaction(contract, functionName, args = [], options = {}) {
        const nonce = await this.getNextNonce();
        const tx = await contract[functionName](...args, { ...options, nonce });
        return await this.waitForTransaction(tx);
    }
}

async function comprehensiveTestWithNonceManager() {
    // Conectar ao provider
    const provider = new ethers.JsonRpcProvider('http://127.0.0.1:8545');
    
    // Criar wallet com a chave privada do owner
    const privateKey = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80';
    const wallet = new ethers.Wallet(privateKey, provider);
    
    // Endereço do contrato
    const contractAddress = '0x5FbDB2315678afecb367f032d93F642f64180aa3';
    
    // ABI atualizado
    const abi = [
        "function owner() external view returns (address)",
        "function totalCbsds() external view returns (uint256)",
        "function totalGrants() external view returns (uint256)",
        "function authorizedSAS(address) external view returns (bool)",
        "function authorizeSAS(address _sas) external",
        "function revokeSAS(address _sas) external",
        "function registration((string,string,string,string,string,string,string[],uint256,int256,int256,uint256,string,bool,uint256,uint256,uint256,string,string)) external",
        "function grant((string,string,string,uint256,uint256,uint256,uint256,uint256,uint256,uint256)) external",
        "function relinquishment(string,string,string) external",
        "function deregistration(string,string) external"
    ];
    
    // Instanciar contrato
    const contract = new ethers.Contract(contractAddress, abi, wallet);
    
    // Criar gerenciador de nonce
    const nonceManager = new NonceManager(provider, wallet);
    
    try {
        console.log('🧪 TESTE INTEGRAÇÃO SASSharedRegistry');
        console.log('=============================================');
        
        // 1. Verificar estado inicial
        console.log('\n📊 Estado Inicial:');
        const owner = await contract.owner();
        console.log('  - Owner:', owner);
        console.log('  - Owner autorizado como SAS:', await contract.authorizedSAS(owner));
        
        // 2. Testar IDs únicos
        const timestamp = Math.floor(Date.now() / 1000);
        const fccId = `TEST${timestamp}`;
        const userId = `USER${timestamp}`;
        const cbsdSerialNumber = `SN${timestamp}`;
        
        // 3. Testar Registro
        console.log('\n📝 Testando Registro de CBSD:');
        // Ordem dos campos conforme struct RegistrationRequest
        const registrationArgs = [
            fccId, // string fccId
            userId, // string userId
            cbsdSerialNumber, // string cbsdSerialNumber
            'CALL', // string callSign
            'A', // string cbsdCategory
            'E-UTRA', // string airInterface
            ['EUTRA_CARRIER_RSSI_ALWAYS'], // string[] measCapability
            47, // uint256 eirpCapability
            375000000, // int256 latitude
            1224000000, // int256 longitude
            30, // uint256 height
            'AGL', // string heightType
            false, // bool indoorDeployment
            15, // uint256 antennaGain
            360, // uint256 antennaBeamwidth
            0, // uint256 antennaAzimuth
            '', // string groupingParam
            wallet.address // string cbsdAddress
        ];
        await nonceManager.sendTransaction(contract, 'registration', [registrationArgs]);
        
        // 4. Testar Grant
        console.log('\n📝 Testando Criação de Grant:');
        // Ordem dos campos conforme struct GrantRequest
        const grantArgs = [
            fccId, // string fccId
            cbsdSerialNumber, // string cbsdSerialNumber
            'GAA', // string channelType
            47, // uint256 maxEirp
            3550000000, // uint256 lowFrequency
            3700000000, // uint256 highFrequency
            47, // uint256 requestedMaxEirp
            3550000000, // uint256 requestedLowFrequency
            3700000000, // uint256 requestedHighFrequency
            Math.floor(Date.now() / 1000) + 3600 // uint256 grantExpireTime
        ];
        await nonceManager.sendTransaction(contract, 'grant', [grantArgs]);
        
        // 5. Testar Relinquishment
        console.log('\n📝 Testando Relinquishment:');
        // grantId gerado conforme lógica do contrato
        const grantId = `grant_${fccId}${cbsdSerialNumber}0`;
        await nonceManager.sendTransaction(contract, 'relinquishment', [fccId, cbsdSerialNumber, grantId]);
        
        // 6. Testar Deregistration
        console.log('\n📝 Testando Deregistration:');
        await nonceManager.sendTransaction(contract, 'deregistration', [fccId, cbsdSerialNumber]);
        
        // 7. Testar Autorização e Revogação de SAS
        console.log('\n📝 Testando Autorização de SAS:');
        const testSAS = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8';
        await nonceManager.sendTransaction(contract, 'authorizeSAS', [testSAS]);
        const isAuthorized = await contract.authorizedSAS(testSAS);
        console.log('  - SAS autorizado:', isAuthorized);
        await nonceManager.sendTransaction(contract, 'revokeSAS', [testSAS]);
        const isAuthorizedAfter = await contract.authorizedSAS(testSAS);
        console.log('  - SAS autorizado após revogação:', isAuthorizedAfter);
        
        console.log('\n✅ Todos os testes de integração executados com sucesso!');
    } catch (err) {
        console.error('❌ Erro durante o teste de integração:', err);
    }
}

comprehensiveTestWithNonceManager(); 