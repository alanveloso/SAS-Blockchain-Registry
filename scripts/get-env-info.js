const hre = require("hardhat");

async function main() {
  console.log("🔍 Obtendo informações para o .env...");

  // Obter a primeira conta (que tem ETH)
  const [deployer] = await hre.ethers.getSigners();
  
  console.log("👤 Conta:", deployer.address);
  console.log("🔑 Chave privada:", deployer.privateKey);
  console.log("💰 Saldo:", await hre.ethers.provider.getBalance(deployer.address));

  // Fazer deploy do contrato
  const SASSharedRegistry = await hre.ethers.getContractFactory("SASSharedRegistry");
  const sasSharedRegistry = await SASSharedRegistry.deploy();
  await sasSharedRegistry.waitForDeployment();
  const address = await sasSharedRegistry.getAddress();

  console.log("\n📋 Configurações para o .env:");
  console.log("RPC_URL=http://127.0.0.1:8545");
  console.log(`CONTRACT_ADDRESS=${address}`);
  console.log(`OWNER_PRIVATE_KEY=${deployer.privateKey}`);
  console.log("CHAIN_ID=31337");
  console.log("GAS_LIMIT=3000000");
  console.log("POLLING_INTERVAL=2");
  console.log("LOG_LEVEL=INFO");

  console.log("\n📄 Conteúdo completo do .env:");
  console.log("RPC_URL=http://127.0.0.1:8545");
  console.log(`CONTRACT_ADDRESS=${address}`);
  console.log(`OWNER_PRIVATE_KEY=${deployer.privateKey}`);
  console.log("CHAIN_ID=31337");
  console.log("GAS_LIMIT=3000000");
  console.log("POLLING_INTERVAL=2");
  console.log("LOG_LEVEL=INFO");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 