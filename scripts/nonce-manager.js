const { ethers } = require('ethers');

/**
 * Gerenciador automático de nonce para evitar problemas de transações
 * em redes com automining habilitado
 */
class NonceManager {
    constructor(provider, wallet) {
        this.provider = provider;
        this.wallet = wallet;
        this.currentNonce = null;
        this.pendingTransactions = new Set();
    }

    /**
     * Obtém o próximo nonce disponível
     */
    async getNextNonce() {
        if (this.currentNonce === null) {
            this.currentNonce = await this.provider.getTransactionCount(this.wallet.address);
        } else {
            this.currentNonce++;
        }
        return this.currentNonce;
    }

    /**
     * Aguarda a confirmação de uma transação
     */
    async waitForTransaction(tx, description = 'Transação') {
        try {
            const receipt = await tx.wait();
            console.log(`  ✅ ${description} confirmada no bloco ${receipt.blockNumber}`);
            return receipt;
        } catch (error) {
            console.error(`  ❌ Erro na ${description}:`, error.message);
            throw error;
        }
    }

    /**
     * Envia uma transação com nonce automático
     */
    async sendTransaction(contract, functionName, args = [], description = null) {
        const nonce = await this.getNextNonce();
        const txHash = `${functionName}_${nonce}`;
        
        if (this.pendingTransactions.has(txHash)) {
            throw new Error(`Transação ${txHash} já está pendente`);
        }
        
        this.pendingTransactions.add(txHash);
        
        try {
            const tx = await contract[functionName](...args, { nonce });
            const receipt = await this.waitForTransaction(tx, description || functionName);
            this.pendingTransactions.delete(txHash);
            return receipt;
        } catch (error) {
            this.pendingTransactions.delete(txHash);
            throw error;
        }
    }

    /**
     * Executa múltiplas transações em sequência
     */
    async sendMultipleTransactions(transactions) {
        const results = [];
        for (const tx of transactions) {
            const result = await this.sendTransaction(
                tx.contract, 
                tx.functionName, 
                tx.args, 
                tx.description
            );
            results.push(result);
        }
        return results;
    }

    /**
     * Reseta o nonce para o valor atual da rede
     */
    async resetNonce() {
        this.currentNonce = await this.provider.getTransactionCount(this.wallet.address);
        this.pendingTransactions.clear();
        console.log(`  🔄 Nonce resetado para: ${this.currentNonce}`);
    }

    /**
     * Obtém estatísticas do gerenciador
     */
    getStats() {
        return {
            currentNonce: this.currentNonce,
            pendingTransactions: this.pendingTransactions.size
        };
    }
}

/**
 * Utilitário para criar testes com gerenciador de nonce
 */
class TestHelper {
    constructor(provider, wallet, contractAddress, abi) {
        this.provider = provider;
        this.wallet = wallet;
        this.contract = new ethers.Contract(contractAddress, abi, wallet);
        this.nonceManager = new NonceManager(provider, wallet);
    }

    /**
     * Executa um teste completo do fluxo SAS
     */
    async runFullSASFlow() {
        console.log('🧪 TESTE COMPLETO DO FLUXO SAS');
        console.log('==============================');
        
        try {
            // 1. Verificar estado inicial
            await this.checkInitialState();
            
            // 2. Criar dados únicos
            const testData = this.createUniqueTestData();
            
            // 3. Executar fluxo completo
            await this.executeRegistrationFlow(testData);
            await this.executeGrantFlow(testData);
            await this.executeHeartbeatFlow(testData);
            await this.executeRelinquishmentFlow(testData);
            await this.executeAdminFlow(testData);
            await this.executeDeregistrationFlow(testData);
            
            // 4. Verificar estado final
            await this.checkFinalState();
            
            console.log('\n🎉 FLUXO COMPLETO EXECUTADO COM SUCESSO!');
            
        } catch (error) {
            console.error('❌ Erro no fluxo:', error.message);
            throw error;
        }
    }

    async checkInitialState() {
        console.log('\n📊 Estado Inicial:');
        const owner = await this.contract.owner();
        const isAuthorized = await this.contract.authorizedSAS(owner);
        console.log('  - Owner:', owner);
        console.log('  - Owner autorizado como SAS:', isAuthorized);
    }

    createUniqueTestData() {
        const timestamp = Math.floor(Date.now() / 1000);
        return {
            fccId: ethers.zeroPadValue(ethers.toUtf8Bytes(`TEST${timestamp}`), 32),
            userId: ethers.zeroPadValue(ethers.toUtf8Bytes(`USER${timestamp}`), 32),
            cbsdSerialNumber: ethers.zeroPadValue(ethers.toUtf8Bytes(`SN${timestamp}`), 32),
            timestamp
        };
    }

    async executeRegistrationFlow(testData) {
        console.log('\n📝 Fluxo de Registro:');
        
        // Injetar IDs
        await this.nonceManager.sendTransaction(
            this.contract, 'InjectFccId', 
            [testData.fccId, 47], 
            'Injeção de FCC ID'
        );
        
        await this.nonceManager.sendTransaction(
            this.contract, 'InjectUserId', 
            [testData.userId], 
            'Injeção de User ID'
        );
        
        // Registrar CBSD
        const registrationData = this.createRegistrationData(testData);
        await this.nonceManager.sendTransaction(
            this.contract, 'Registration', 
            [registrationData], 
            'Registro de CBSD'
        );
        
        // Verificar registro
        const isRegistered = await this.contract.isCBSDRegistered(testData.fccId, testData.cbsdSerialNumber);
        console.log('  - CBSD registrado:', isRegistered);
    }

    async executeGrantFlow(testData) {
        console.log('\n📝 Fluxo de Grant:');
        
        const grantData = this.createGrantData(testData);
        await this.nonceManager.sendTransaction(
            this.contract, 'GrantSpectrum', 
            [grantData], 
            'Criação de Grant'
        );
        
        // Verificar grant
        const grants = await this.contract.getGrants(testData.fccId, testData.cbsdSerialNumber);
        console.log('  - Total de grants:', grants.length);
        
        if (grants.length > 0) {
            const grant = grants[0];
            console.log('  - Grant ID:', grant.grantId);
            console.log('  - Channel Type:', ethers.toUtf8String(grant.channelType).replace(/\0/g, ''));
            console.log('  - Max EIRP:', grant.maxEirp.toString());
            console.log('  - Low Frequency:', grant.lowFrequency.toString());
            console.log('  - High Frequency:', grant.highFrequency.toString());
            
            // Verificar valores
            console.log('  ✅ Valores corretos:', 
                grant.maxEirp.toString() === '47' && 
                grant.lowFrequency.toString() === '3550000000' && 
                grant.highFrequency.toString() === '3700000000' ? 'SIM' : 'NÃO'
            );
        }
    }

    async executeHeartbeatFlow(testData) {
        console.log('\n📝 Fluxo de Heartbeat:');
        
        const grants = await this.contract.getGrants(testData.fccId, testData.cbsdSerialNumber);
        if (grants.length > 0) {
            const grantId = grants[0].grantId;
            await this.contract.Heartbeat(testData.fccId, testData.cbsdSerialNumber, grantId);
            console.log('  ✅ Heartbeat executado');
        }
    }

    async executeRelinquishmentFlow(testData) {
        console.log('\n📝 Fluxo de Relinquishment:');
        
        const grants = await this.contract.getGrants(testData.fccId, testData.cbsdSerialNumber);
        if (grants.length > 0) {
            const grantId = grants[0].grantId;
            await this.nonceManager.sendTransaction(
                this.contract, 'Relinquishment', 
                [testData.fccId, testData.cbsdSerialNumber, grantId], 
                'Terminação de Grant'
            );
            
            const updatedGrants = await this.contract.getGrants(testData.fccId, testData.cbsdSerialNumber);
            console.log('  - Grant terminado:', updatedGrants[0].terminated);
        }
    }

    async executeAdminFlow(testData) {
        console.log('\n📝 Fluxo Administrativo:');
        
        // Blacklist
        const testFccId = ethers.zeroPadValue(ethers.toUtf8Bytes('BLACKLIST'), 32);
        await this.nonceManager.sendTransaction(
            this.contract, 'BlacklistByFccId', 
            [testFccId], 
            'Blacklist FCC ID'
        );
        
        await this.nonceManager.sendTransaction(
            this.contract, 'BlacklistByFccIdAndSerialNumber', 
            [testData.fccId, testData.cbsdSerialNumber], 
            'Blacklist Serial Number'
        );
        
        // SAS Authorization
        const testSAS = '0x70997970C51812dc3A010C7d01b50e0d17dc79C8';
        await this.nonceManager.sendTransaction(
            this.contract, 'authorizeSAS', 
            [testSAS], 
            'Autorização de SAS'
        );
        
        const isAuthorized = await this.contract.authorizedSAS(testSAS);
        console.log('  - SAS autorizado:', isAuthorized);
        
        await this.nonceManager.sendTransaction(
            this.contract, 'revokeSAS', 
            [testSAS], 
            'Revogação de SAS'
        );
    }

    async executeDeregistrationFlow(testData) {
        console.log('\n📝 Fluxo de Deregistration:');
        
        await this.nonceManager.sendTransaction(
            this.contract, 'Deregistration', 
            [testData.fccId, testData.cbsdSerialNumber], 
            'Deregistration de CBSD'
        );
        
        const isStillRegistered = await this.contract.isCBSDRegistered(testData.fccId, testData.cbsdSerialNumber);
        console.log('  - CBSD ainda registrado:', isStillRegistered);
    }

    async checkFinalState() {
        console.log('\n📊 Estado Final:');
        const totalCbsds = await this.contract.totalCbsds();
        const totalGrants = await this.contract.totalGrants();
        console.log('  - Total CBSDs:', totalCbsds.toString());
        console.log('  - Total Grants:', totalGrants.toString());
        
        const stats = this.nonceManager.getStats();
        console.log('  - Nonce atual:', stats.currentNonce);
        console.log('  - Transações pendentes:', stats.pendingTransactions);
    }

    createRegistrationData(testData) {
        return {
            fccId: testData.fccId,
            userId: testData.userId,
            cbsdSerialNumber: testData.cbsdSerialNumber,
            callSign: ethers.zeroPadValue(ethers.toUtf8Bytes('CALL'), 32),
            cbsdCategory: ethers.zeroPadValue(ethers.toUtf8Bytes('A'), 32),
            airInterface: ethers.zeroPadValue(ethers.toUtf8Bytes('E_UTRA'), 32),
            measCapability: [ethers.zeroPadValue(ethers.toUtf8Bytes('EUTRA_CARRIER_RSSI_ALWAYS'), 32)],
            eirpCapability: 47,
            latitude: 375000000,
            longitude: 1224000000,
            height: 30,
            heightType: ethers.zeroPadValue(ethers.toUtf8Bytes('AGL'), 32),
            indoorDeployment: false,
            antennaGain: 15,
            antennaBeamwidth: 360,
            antennaAzimuth: 0,
            groupingParam: ethers.zeroPadValue(ethers.toUtf8Bytes(''), 32),
            cbsdAddress: this.wallet.address
        };
    }

    createGrantData(testData) {
        return {
            fccId: testData.fccId,
            cbsdSerialNumber: testData.cbsdSerialNumber,
            channelType: ethers.zeroPadValue(ethers.toUtf8Bytes('GAA'), 32),
            maxEirp: 47,
            lowFrequency: 3550000000,
            highFrequency: 3700000000,
            requestedMaxEirp: 47,
            requestedLowFrequency: 3550000000,
            requestedHighFrequency: 3700000000,
            grantExpireTime: Math.floor(Date.now() / 1000) + 3600
        };
    }
}

// Exportar classes para uso em outros scripts
module.exports = { NonceManager, TestHelper }; 