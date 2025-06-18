const { Contract } = require('@hyperledger/caliper-core');
const { assert } = require('chai');

async function beforeTest() {
    const contract = await Contract.createInstance('network-config.yaml', 'CBSDRegistry');
    return contract;
}

async function runBenchmark(contract) {
    // Teste de registro de CBSD
    const startRegister = Date.now();
    await contract.submitTransaction('registerCBSD', '1', '0x1234...', '1000');
    const endRegister = Date.now();
    console.log(`Registro de CBSD executado em ${endRegister - startRegister}ms`);

    // Teste de atualização de grant
    const startUpdateGrant = Date.now();
    await contract.submitTransaction('updateGrantAmount', '1', '2000');
    const endUpdateGrant = Date.now();
    console.log(`Atualização de Grant executada em ${endUpdateGrant - startUpdateGrant}ms`);
}

module.exports.beforeTest = beforeTest;
module.exports.runBenchmark = runBenchmark;

