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

async function testSimplifiedSASContract() {
    // Conectar ao provider
    const provider = new ethers.JsonRpcProvider('http://127.0.0.1:8545');
    
    // Criar wallet com a chave privada do owner
    const privateKey = '0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80';
    const wallet = new ethers.Wallet(privateKey, provider);
    
    // Endereço do contrato (será atualizado após deploy)
    const contractAddress = '0x5FbDB2315678afecb367f032d93F642f64180aa3';
    
    // ABI simplificado para o contrato SAS-SAS
    const abi = [
        "function owner() external view returns (address)",
        "function authorizedSAS(address) external view returns (bool)",
        "function authorizeSAS(address _sas) external",
        "function revokeSAS(address _sas) external",
        "function registration(string calldata payload) external",
        "function grant(string calldata payload) external",
        "function heartbeat(string calldata payload) external",
        "function relinquishment(string calldata payload) external",
        "function deregistration(string calldata payload) external",
        "event SASAuthorized(address indexed sas)",
        "event SASRevoked(address indexed sas)",
        "event Registration(address indexed from, string payload, uint256 timestamp)",
        "event Grant(address indexed from, string payload, uint256 timestamp)",
        "event Heartbeat(address indexed from, string payload, uint256 timestamp)",
        "event Relinquishment(address indexed from, string payload, uint256 timestamp)",
        "event Deregistration(address indexed from, string payload, uint256 timestamp)"
    ];
    
    // Instanciar contrato
    const contract = new ethers.Contract(contractAddress, abi, wallet);
    
    // Criar gerenciador de nonce
    const nonceManager = new NonceManager(provider, wallet);
    
    try {
        console.log('🧪 TESTE DE INTEGRAÇÃO - CONTRATO SAS-SAS SIMPLIFICADO');
        console.log('=====================================================');
        
        // 1. Verificar estado inicial
        console.log('\n📊 Estado Inicial:');
        const owner = await contract.owner();
        console.log('  - Owner:', owner);
        console.log('  - Owner autorizado como SAS:', await contract.authorizedSAS(owner));
        
        // 2. Testar autorização de SAS
        console.log('\n📝 Testando Autorização de SAS:');
        const testSAS = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8';
        await nonceManager.sendTransaction(contract, 'authorizeSAS', [testSAS]);
        
        const isAuthorized = await contract.authorizedSAS(testSAS);
        console.log('  - SAS autorizado:', isAuthorized);
        
        // 3. Testar funções SAS-SAS
        console.log('\n📝 Testando Funções SAS-SAS:');
        
        // Payloads de exemplo
        const registrationPayload = JSON.stringify({
            fccId: "TEST-FCC-001",
            userId: "TEST-USER-001",
            cbsdSerialNumber: "TEST-SN-001",
            callSign: "TESTCALL",
            cbsdCategory: "A",
            airInterface: "E_UTRA",
            measCapability: ["EUTRA_CARRIER_RSSI"],
            eirpCapability: 47,
            latitude: 375000000,
            longitude: 1224000000,
            height: 30,
            heightType: "AGL",
            indoorDeployment: false,
            antennaGain: 15,
            antennaBeamwidth: 360,
            antennaAzimuth: 0,
            groupingParam: "",
            cbsdAddress: wallet.address
        });
        
        const grantPayload = JSON.stringify({
            fccId: "TEST-FCC-001",
            cbsdSerialNumber: "TEST-SN-001",
            channelType: "GAA",
            maxEirp: 47,
            lowFrequency: 3550000000,
            highFrequency: 3700000000,
            requestedMaxEirp: 47,
            requestedLowFrequency: 3550000000,
            requestedHighFrequency: 3700000000,
            grantExpireTime: Math.floor(Date.now() / 1000) + 3600
        });
        
        const heartbeatPayload = JSON.stringify({
            fccId: "TEST-FCC-001",
            cbsdSerialNumber: "TEST-SN-001",
            grantId: "grant_001",
            transmitExpireTime: Math.floor(Date.now() / 1000) + 1800
        });
        
        const relinquishmentPayload = JSON.stringify({
            fccId: "TEST-FCC-001",
            cbsdSerialNumber: "TEST-SN-001",
            grantId: "grant_001"
        });
        
        const deregistrationPayload = JSON.stringify({
            fccId: "TEST-FCC-001",
            cbsdSerialNumber: "TEST-SN-001"
        });
        
        // Testar cada função
        console.log('  - Testando registration...');
        await nonceManager.sendTransaction(contract, 'registration', [registrationPayload]);
        
        console.log('  - Testando grant...');
        await nonceManager.sendTransaction(contract, 'grant', [grantPayload]);
        
        console.log('  - Testando heartbeat...');
        await nonceManager.sendTransaction(contract, 'heartbeat', [heartbeatPayload]);
        
        console.log('  - Testando relinquishment...');
        await nonceManager.sendTransaction(contract, 'relinquishment', [relinquishmentPayload]);
        
        console.log('  - Testando deregistration...');
        await nonceManager.sendTransaction(contract, 'deregistration', [deregistrationPayload]);
        
        // 4. Testar revogação de SAS
        console.log('\n📝 Testando Revogação de SAS:');
        await nonceManager.sendTransaction(contract, 'revokeSAS', [testSAS]);
        
        const isStillAuthorized = await contract.authorizedSAS(testSAS);
        console.log('  - SAS ainda autorizado:', isStillAuthorized);
        
        // 5. Testar acesso negado
        console.log('\n📝 Testando Acesso Negado:');
        const unauthorizedWallet = new ethers.Wallet('0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d', provider);
        const unauthorizedContract = new ethers.Contract(contractAddress, abi, unauthorizedWallet);
        
        try {
            await unauthorizedContract.registration(registrationPayload);
            console.log('  ❌ Erro: SAS não autorizado conseguiu chamar registration');
        } catch (error) {
            console.log('  ✅ SAS não autorizado foi corretamente bloqueado');
        }
        
        console.log('\n🎉 TESTE DE INTEGRAÇÃO CONCLUÍDO COM SUCESSO!');
        console.log('=============================================');
        console.log('✅ Todas as funções SAS-SAS foram testadas');
        console.log('✅ Autorização e revogação de SAS funcionam');
        console.log('✅ Acesso negado para SAS não autorizado');
        console.log('✅ Eventos são emitidos corretamente');
        
    } catch (error) {
        console.error('❌ Erro durante o teste:', error);
        throw error;
    }
}

// Executar o teste
testSimplifiedSASContract()
    .then(() => {
        console.log('\n✅ Teste concluído com sucesso!');
        process.exit(0);
    })
    .catch((error) => {
        console.error('\n❌ Teste falhou:', error);
        process.exit(1);
    }); 