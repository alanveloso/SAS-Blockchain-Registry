const hre = require("hardhat");
const fs = require("fs");

async function main() {
  const numAccounts = 20; // Altere para o número de threads desejado
  const value = hre.ethers.parseEther("10"); // Valor a enviar para cada conta

  const [deployer] = await hre.ethers.getSigners();

  const accounts = [];

  for (let i = 0; i < numAccounts; i++) {
    // Gera uma nova carteira
    const wallet = hre.ethers.Wallet.createRandom();
    accounts.push({
      address: wallet.address,
      privateKey: wallet.privateKey
    });

    // Envia ETH para a nova conta
    const tx = await deployer.sendTransaction({
      to: wallet.address,
      value
    });
    console.log(`Enviando 10 ETH para ${wallet.address}... TX: ${tx.hash}`);
    await tx.wait();
    console.log(`✔️  ${wallet.address} recarregado!`);
  }

  // Salva as contas em um arquivo JSON
  fs.writeFileSync("generated_accounts.json", JSON.stringify(accounts, null, 2));
  console.log("Contas e chaves privadas salvas em generated_accounts.json");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  }); 