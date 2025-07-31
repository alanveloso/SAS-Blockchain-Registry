const hre = require("hardhat");

async function main() {
  console.log("🚀 Fazendo deploy do SASSharedRegistry...");

  const SASSharedRegistry = await hre.ethers.getContractFactory("SASSharedRegistry");
  const sasSharedRegistry = await SASSharedRegistry.deploy();

  await sasSharedRegistry.waitForDeployment();

  const address = await sasSharedRegistry.getAddress();
  console.log("✅ SASSharedRegistry deployado em:", address);

  // Obter informações da conta que fez o deploy
  const [deployer] = await hre.ethers.getSigners();
  console.log("👤 Conta que fez o deploy:", deployer.address);
  console.log("💰 Saldo da conta:", await hre.ethers.provider.getBalance(deployer.address));

  const network = await hre.ethers.provider.getNetwork();
  console.log("\n📋 Configurações para o .env:");
  console.log(`RPC_URL=http://127.0.0.1:8545`);
  console.log(`CONTRACT_ADDRESS=${address}`);
  console.log(`OWNER_PRIVATE_KEY=${deployer.privateKey}`);
  console.log(`CHAIN_ID=${network.chainId}`);

  return address;
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 