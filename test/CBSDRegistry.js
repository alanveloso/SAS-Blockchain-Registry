const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CBSDRegistry", function () {
  let CBSDRegistry, cbsdRegistry, owner, other;

  beforeEach(async function () {
    [owner, other] = await ethers.getSigners();
    CBSDRegistry = await ethers.getContractFactory("CBSDRegistry");
    cbsdRegistry = await CBSDRegistry.deploy();
  });

  it("deve definir o owner corretamente", async function () {
    expect(await cbsdRegistry.owner()).to.equal(owner.address);
  });

  it("deve registrar um novo CBSD", async function () {
    await expect(cbsdRegistry.registerCBSD(1, other.address, 1000))
      .to.emit(cbsdRegistry, "CBSDRegistered")
      .withArgs(1, other.address, 1000);
    const info = await cbsdRegistry.getCBSDInfo(1);
    expect(info[0]).to.equal(other.address);
    expect(info[1]).to.equal(1000);
    expect(info[2]).to.equal("registered");
  });

  it("não deve permitir registrar CBSD já registrado", async function () {
    await cbsdRegistry.registerCBSD(1, other.address, 1000);
    await expect(
      cbsdRegistry.registerCBSD(1, other.address, 2000)
    ).to.be.revertedWith("CBSD already registered.");
  });

  it("não deve permitir registro por não-owner", async function () {
    await expect(
      cbsdRegistry.connect(other).registerCBSD(2, other.address, 1000)
    ).to.be.revertedWith("Not authorized");
  });

  it("deve atualizar o grant amount de um CBSD", async function () {
    await cbsdRegistry.registerCBSD(1, other.address, 1000);
    await expect(cbsdRegistry.updateGrantAmount(1, 2000))
      .to.emit(cbsdRegistry, "GrantAmountUpdated")
      .withArgs(1, 2000);
    const info = await cbsdRegistry.getCBSDInfo(1);
    expect(info[1]).to.equal(2000);
  });

  it("não deve permitir atualizar grant de CBSD inexistente", async function () {
    await expect(
      cbsdRegistry.updateGrantAmount(99, 2000)
    ).to.be.revertedWith("CBSD not registered.");
  });

  it("não deve permitir atualização de grant por não-owner", async function () {
    await cbsdRegistry.registerCBSD(1, other.address, 1000);
    await expect(
      cbsdRegistry.connect(other).updateGrantAmount(1, 2000)
    ).to.be.revertedWith("Not authorized");
  });

  it("deve atualizar o status de um CBSD", async function () {
    await cbsdRegistry.registerCBSD(1, other.address, 1000);
    await expect(cbsdRegistry.updateStatus(1, "active"))
      .to.emit(cbsdRegistry, "StatusUpdated")
      .withArgs(1, "active");
    const info = await cbsdRegistry.getCBSDInfo(1);
    expect(info[2]).to.equal("active");
  });

  it("não deve permitir atualizar status de CBSD inexistente", async function () {
    await expect(
      cbsdRegistry.updateStatus(99, "inactive")
    ).to.be.revertedWith("CBSD not registered.");
  });

  it("não deve permitir atualização de status por não-owner", async function () {
    await cbsdRegistry.registerCBSD(1, other.address, 1000);
    await expect(
      cbsdRegistry.connect(other).updateStatus(1, "inactive")
    ).to.be.revertedWith("Not authorized");
  });
}); 