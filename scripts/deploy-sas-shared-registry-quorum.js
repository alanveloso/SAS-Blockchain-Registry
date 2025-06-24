const path = require('path');
const fs = require('fs-extra');
var ethers = require('ethers');

// RPCNODE details
const { tessera, besu } = require("./keys.js");
const host = besu.rpcnode.url;
const accountPrivateKey = besu.rpcnode.accountPrivateKey;

// abi and bytecode generated from SASSharedRegistry.sol:
const contractJsonPath = path.resolve(__dirname, '../','artifacts','contracts','SASSharedRegistry.sol','SASSharedRegistry.json');
const contractJson = JSON.parse(fs.readFileSync(contractJsonPath));
const contractAbi = contractJson.abi;
const contractBytecode = contractJson.bytecode;

async function main(){
  console.log("🚀 Fazendo deploy do SASSharedRegistry usando Quorum Dev Quickstart...");
  
  const provider = new ethers.JsonRpcProvider(host);
  const wallet = new ethers.Wallet(accountPrivateKey, provider);

  console.log("👤 Conta que fará o deploy:", wallet.address);
  
  // Verificar saldo da conta
  const balance = await provider.getBalance(wallet.address);
  console.log("💰 Saldo da conta:", ethers.formatEther(balance), "ETH");

  try {
    const factory = new ethers.ContractFactory(contractAbi, contractBytecode, wallet);
    console.log("📦 Criando contrato...");
    
    const contract = await factory.deploy();
    console.log("⏳ Aguardando confirmação do deploy...");
    
    // Aguardar o deploy ser confirmado
    const deployed = await contract.waitForDeployment();
    const address = await deployed.getAddress();
    
    console.log("✅ SASSharedRegistry deployado em:", address);
    console.log("👤 Conta que fez o deploy:", wallet.address);
    console.log("💰 Saldo final da conta:", ethers.formatEther(await provider.getBalance(wallet.address)), "ETH");

    console.log("\n📋 Configurações para o .env:");
    console.log(`RPC_URL=${host}`);
    console.log(`CONTRACT_ADDRESS=${address}`);
    console.log(`OWNER_PRIVATE_KEY=${accountPrivateKey}`);
    console.log(`CHAIN_ID=1337`);

    return address;
  } catch (error) {
    console.error("❌ Erro no deploy:", error.message);
    throw error;
  }
}

if (require.main === module) {
  main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
    });
}

module.exports = exports = main; 