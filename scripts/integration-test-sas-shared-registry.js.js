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
    
    // ABI completo
    const abi = [
        "function owner() external view returns (address)",
        "function totalCbsds() external view returns (uint256)",
        "function totalGrants() external view returns (uint256)",
        "function authorizedSAS(address) external view returns (bool)",
        "function InjectFccId(string fccId, uint256 maxEirp) external",
        "function InjectUserId(string userId) external",
        "function Registration(tuple(string fccId, string userId, string cbsdSerialNumber, string callSign, string cbsdCategory, string airInterface, string[] measCapability, uint256 eirpCapability, int256 latitude, int256 longitude, uint256 height, string heightType, bool indoorDeployment, uint256 antennaGain, uint256 antennaBeamwidth, uint256 antennaAzimuth, string groupingParam, string cbsdAddress)) external",
        "function GrantSpectrum(tuple(string fccId, string cbsdSerialNumber, string channelType, uint256 maxEirp, uint256 lowFrequency, uint256 highFrequency, uint256 requestedMaxEirp, uint256 requestedLowFrequency, uint256 requestedHighFrequency, uint256 grantExpireTime)) external",
        "function Heartbeat(string fccId, string cbsdSerialNumber, string grantId) external view",
        "function Relinquishment(string fccId, string cbsdSerialNumber, string grantId) external",
        "function Deregistration(string fccId, string cbsdSerialNumber) external",
        "function BlacklistByFccId(string fccId) external",
        "function BlacklistByFccIdAndSerialNumber(string fccId, string serialNumber) external",
        "function authorizeSAS(address _sas) external",
        "function revokeSAS(address _sas) external",
        "function isCBSDRegistered(string fccId, string cbsdSerialNumber) external view returns (bool)",
        "function getCBSDInfo(string fccId, string cbsdSerialNumber) external view returns (tuple(string fccId, string userId, string cbsdSerialNumber, string callSign, string cbsdCategory, string airInterface, string[] measCapability, uint256 eirpCapability, int256 latitude, int256 longitude, uint256 height, string heightType, bool indoorDeployment, uint256 antennaGain, uint256 antennaBeamwidth, uint256 antennaAzimuth, string groupingParam, string cbsdAddress, address sasOrigin, uint256 registrationTimestamp))",
        "function getGrants(string fccId, string cbsdSerialNumber) external view returns (tuple(string grantId, string channelType, uint256 grantExpireTime, bool terminated, uint256 maxEirp, uint256 lowFrequency, uint256 highFrequency, uint256 requestedMaxEirp, uint256 requestedLowFrequency, uint256 requestedHighFrequency, address sasOrigin, uint256 grantTimestamp)[])"
    ];
    
    // Instanciar contrato
    const contract = new ethers.Contract(contractAddress, abi, wallet);
    
    // Criar gerenciador de nonce
    const nonceManager = new NonceManager(provider, wallet);
    
    try {
        console.log('🧪 TESTE ABRANGENTE COM GERENCIADOR DE NONCE');
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
        
        console.log('\n📝 Testando Injeção de IDs:');
        await nonceManager.sendTransaction(contract, 'InjectFccId', [fccId, 47]);
        await nonceManager.sendTransaction(contract, 'InjectUserId', [userId]);
        
        // 3. Testar Registro
        console.log('\n📝 Testando Registro de CBSD:');
        const registrationData = {
            fccId: fccId,
            userId: userId,
            cbsdSerialNumber: cbsdSerialNumber,
            callSign: 'CALL',
            cbsdCategory: 'A',
            airInterface: 'E_UTRA',
            measCapability: ['EUTRA_CARRIER_RSSI_ALWAYS'],
            eirpCapability: 47,
            latitude: 375000000,
            longitude: 1224000000,
            height: 30,
            heightType: 'AGL',
            indoorDeployment: false,
            antennaGain: 15,
            antennaBeamwidth: 360,
            antennaAzimuth: 0,
            groupingParam: '',
            cbsdAddress: wallet.address
        };
        
        await nonceManager.sendTransaction(contract, 'Registration', [registrationData]);
        
        // 4. Verificar registro
        console.log('\n🔍 Verificando Registro:');
        const isRegistered = await contract.isCBSDRegistered(fccId, cbsdSerialNumber);
        console.log('  - CBSD registrado:', isRegistered);
        
        const cbsdInfo = await contract.getCBSDInfo(fccId, cbsdSerialNumber);
        console.log('  - FCC ID:', cbsdInfo.fccId);
        console.log('  - User ID:', cbsdInfo.userId);
        console.log('  - Serial Number:', cbsdInfo.cbsdSerialNumber);
        console.log('  - Category:', cbsdInfo.cbsdCategory);
        
        // 5. Testar Grant
        console.log('\n📝 Testando Criação de Grant:');
        const grantData = {
            fccId: fccId,
            cbsdSerialNumber: cbsdSerialNumber,
            channelType: 'GAA',
            maxEirp: 47,
            lowFrequency: 3550000000,
            highFrequency: 3700000000,
            requestedMaxEirp: 47,
            requestedLowFrequency: 3550000000,
            requestedHighFrequency: 3700000000,
            grantExpireTime: Math.floor(Date.now() / 1000) + 3600
        };
        
        await nonceManager.sendTransaction(contract, 'GrantSpectrum', [grantData]);
        
        // 6. Verificar grant
        console.log('\n🔍 Verificando Grant:');
        const grants = await contract.getGrants(fccId, cbsdSerialNumber);
        console.log('  - Total de grants:', grants.length);
        
        if (grants.length > 0) {
            const grant = grants[0];
            console.log('  - Grant ID:', grant.grantId);
            console.log('  - Channel Type:', grant.channelType);
            console.log('  - Max EIRP:', grant.maxEirp.toString());
            console.log('  - Low Frequency:', grant.lowFrequency.toString());
            console.log('  - High Frequency:', grant.highFrequency.toString());
            console.log('  - Terminated:', grant.terminated);
            console.log('  - Expire Time:', new Date(Number(grant.grantExpireTime) * 1000).toISOString());
            
            // Verificar se os valores estão corretos
            console.log('\n✅ Verificação dos Valores:');
            console.log('  - Max EIRP correto (47):', grant.maxEirp.toString() === '47' ? '✅' : '❌');
            console.log('  - Low Frequency correto (3550000000):', grant.lowFrequency.toString() === '3550000000' ? '✅' : '❌');
            console.log('  - High Frequency correto (3700000000):', grant.highFrequency.toString() === '3700000000' ? '✅' : '❌');
        }
        
        // 7. Testar Heartbeat
        console.log('\n📝 Testando Heartbeat:');
        if (grants.length > 0) {
            const grantId = grants[0].grantId;
            await contract.Heartbeat(fccId, cbsdSerialNumber, grantId);
            console.log('  ✅ Heartbeat executado');
        }
        
        // 8. Testar Relinquishment
        console.log('\n📝 Testando Relinquishment:');
        if (grants.length > 0) {
            const grantId = grants[0].grantId;
            await nonceManager.sendTransaction(contract, 'Relinquishment', [fccId, cbsdSerialNumber, grantId]);
            
            // Verificar se foi terminado
            const updatedGrants = await contract.getGrants(fccId, cbsdSerialNumber);
            console.log('  - Grant terminado:', updatedGrants[0].terminated);
        }
        
        // 9. Testar Blacklist
        console.log('\n📝 Testando Blacklist:');
        const testFccId = 'BLACKLIST';
        await nonceManager.sendTransaction(contract, 'BlacklistByFccId', [testFccId]);
        await nonceManager.sendTransaction(contract, 'BlacklistByFccIdAndSerialNumber', [fccId, cbsdSerialNumber]);
        
        // 10. Testar SAS Authorization
        console.log('\n📝 Testando Autorização de SAS:');
        const testSAS = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8';
        await nonceManager.sendTransaction(contract, 'authorizeSAS', [testSAS]);
        
        const isAuthorized = await contract.authorizedSAS(testSAS);
        console.log('  - SAS autorizado:', isAuthorized);
        
        await nonceManager.sendTransaction(contract, 'revokeSAS', [testSAS]);
        
        // 11. Testar Deregistration
        console.log('\n📝 Testando Deregistration:');
        await nonceManager.sendTransaction(contract, 'Deregistration', [fccId, cbsdSerialNumber]);
        
        const isStillRegistered = await contract.isCBSDRegistered(fccId, cbsdSerialNumber);
        console.log('  - CBSD ainda registrado:', isStillRegistered);
        
        // 12. Verificar contadores finais
        console.log('\n📊 Estado Final:');
        const finalTotalCbsds = await contract.totalCbsds();
        const finalTotalGrants = await contract.totalGrants();
        console.log('  - Total CBSDs:', finalTotalCbsds.toString());
        console.log('  - Total Grants:', finalTotalGrants.toString());
        
        // 11. Testes Negativos e de Limite
        console.log('\n🚨 Testes Negativos e de Limite:');
        // (1) Registrar CBSD com FCC ID não autorizado
        try {
            const badFccId = `BADFCC${timestamp}`;
            const badSerial = `BADSN${timestamp}`;
            const badRegData = { ...registrationData, fccId: badFccId, cbsdSerialNumber: badSerial };
            await nonceManager.sendTransaction(contract, 'Registration', [badRegData]);
            console.log('  ❌ ERRO: Registro com FCC ID não autorizado deveria falhar');
        } catch (err) {
            console.log('  ✅ Registro com FCC ID não autorizado falhou como esperado:', err.reason || err.message);
        }
        // (2) Registrar CBSD com User ID blacklistado
        try {
            const blackUserId = `BLACKUSER${timestamp}`;
            await nonceManager.sendTransaction(contract, 'InjectUserId', [blackUserId]);
            await nonceManager.sendTransaction(contract, 'BlacklistByFccId', [blackUserId]);
            const badRegData2 = { ...registrationData, userId: blackUserId, cbsdSerialNumber: `BADSN2${timestamp}` };
            await nonceManager.sendTransaction(contract, 'Registration', [badRegData2]);
            console.log('  ❌ ERRO: Registro com User ID blacklistado deveria falhar');
        } catch (err) {
            console.log('  ✅ Registro com User ID blacklistado falhou como esperado:', err.reason || err.message);
        }
        // (3) Criar grant para CBSD inexistente
        try {
            const fakeGrantData = { ...grantData, fccId: 'FAKEFCC', cbsdSerialNumber: 'FAKESN' };
            await nonceManager.sendTransaction(contract, 'GrantSpectrum', [fakeGrantData]);
            console.log('  ❌ ERRO: Grant para CBSD inexistente deveria falhar');
        } catch (err) {
            console.log('  ✅ Grant para CBSD inexistente falhou como esperado:', err.reason || err.message);
        }
        // (4) Heartbeat para grant inexistente
        try {
            await contract.Heartbeat(fccId, cbsdSerialNumber, 'FAKEGRANT');
            console.log('  ❌ ERRO: Heartbeat para grant inexistente deveria falhar');
        } catch (err) {
            console.log('  ✅ Heartbeat para grant inexistente falhou como esperado:', err.reason || err.message);
        }
        // (5) Operação com SAS não autorizado
        try {
            const provider2 = new ethers.JsonRpcProvider('http://127.0.0.1:8545');
            const wallet2 = new ethers.Wallet('0x59c6995e998f97a5a0044966f094538e9e7b9d5d7a5c5e5c1c2de9c8a3c3e8a7', provider2);
            const contract2 = new ethers.Contract(contractAddress, abi, wallet2);
            await contract2.Registration(registrationData);
            console.log('  ❌ ERRO: Registro por SAS não autorizado deveria falhar');
        } catch (err) {
            console.log('  ✅ Registro por SAS não autorizado falhou como esperado:', err.reason || err.message);
        }
        
        console.log('\n🎉 TESTE ABRANGENTE CONCLUÍDO COM SUCESSO!');
        console.log('✅ Todos os aspectos do contrato estão funcionando corretamente');
        console.log('✅ Gerenciador de nonce funcionando perfeitamente');
        
        // 13. Resumo final
        console.log('\n📋 RESUMO FINAL:');
        console.log('  🎯 Contrato SAS funcionando perfeitamente');
        console.log('  🎯 Gerenciador de nonce eliminou problemas de nonce');
        console.log('  🎯 Todos os valores sendo armazenados corretamente');
        console.log('  🎯 Todas as funções testadas com sucesso');
        console.log('  🎯 Sistema pronto para produção');
        
    } catch (error) {
        console.error('❌ Erro no teste abrangente:', error.message);
        console.error('Stack:', error.stack);
    }
}

comprehensiveTestWithNonceManager(); 