const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("SASSharedRegistry", function () {
  let SASSharedRegistry, sasSharedRegistry, owner, other;

  beforeEach(async function () {
    [owner, other] = await ethers.getSigners();
    SASSharedRegistry = await ethers.getContractFactory("SASSharedRegistry");
    sasSharedRegistry = await SASSharedRegistry.deploy();
    // Parâmetros padrão para registro
    this.defaultId = 1;
    this.defaultAddress = other.address;
    this.defaultGrant = 1000;
    this.defaultFreq = 3600;
    this.defaultBw = 20;
    this.defaultExpiry = Math.floor(Date.now() / 1000) + 3600;
  });

  it("deve definir o owner corretamente", async function () {
    expect(await sasSharedRegistry.owner()).to.equal(owner.address);
  });

  it("deve registrar um novo CBSD", async function () {
    await expect(sasSharedRegistry.registerCBSD(
      this.defaultId,
      this.defaultAddress,
      this.defaultGrant,
      this.defaultFreq,
      this.defaultBw,
      this.defaultExpiry
    ))
      .to.emit(sasSharedRegistry, "CBSDRegistered")
      .withArgs(this.defaultId, owner.address);
    const info = await sasSharedRegistry.getCBSDInfo(this.defaultId);
    expect(info[0]).to.equal(this.defaultAddress);
    expect(info[1]).to.equal(this.defaultGrant);
    expect(info[2]).to.equal("registered");
  });

  it("não deve permitir registrar CBSD já registrado", async function () {
    await sasSharedRegistry.registerCBSD(
      this.defaultId,
      this.defaultAddress,
      this.defaultGrant,
      this.defaultFreq,
      this.defaultBw,
      this.defaultExpiry
    );
    await expect(
      sasSharedRegistry.registerCBSD(
        this.defaultId,
        this.defaultAddress,
        this.defaultGrant,
        this.defaultFreq,
        this.defaultBw,
        this.defaultExpiry
      )
    ).to.be.revertedWith("CBSD already exists");
  });

  it("não deve permitir registro por não-owner", async function () {
    await expect(
      sasSharedRegistry.connect(other).registerCBSD(
        2,
        this.defaultAddress,
        this.defaultGrant,
        this.defaultFreq,
        this.defaultBw,
        this.defaultExpiry
      )
    ).to.be.revertedWith("Not an authorized SAS");
  });

  it("deve atualizar o grant amount de um CBSD", async function () {
    await sasSharedRegistry.registerCBSD(
      this.defaultId,
      this.defaultAddress,
      this.defaultGrant,
      this.defaultFreq,
      this.defaultBw,
      this.defaultExpiry
    );
    await expect(sasSharedRegistry.updateGrantAmount(this.defaultId, 2000))
      .to.emit(sasSharedRegistry, "GrantAmountUpdated")
      .withArgs(this.defaultId, 2000, owner.address);
    const info = await sasSharedRegistry.getCBSDInfo(this.defaultId);
    expect(info[1]).to.equal(2000);
  });

  it("não deve permitir atualizar grant de CBSD inexistente", async function () {
    await expect(
      sasSharedRegistry.updateGrantAmount(99, 2000)
    ).to.be.revertedWith("CBSD not registered");
  });

  it("não deve permitir atualização de grant por não-owner", async function () {
    await sasSharedRegistry.registerCBSD(
      this.defaultId,
      this.defaultAddress,
      this.defaultGrant,
      this.defaultFreq,
      this.defaultBw,
      this.defaultExpiry
    );
    await expect(
      sasSharedRegistry.connect(other).updateGrantAmount(this.defaultId, 2000)
    ).to.be.revertedWith("Not an authorized SAS");
  });

  it("deve atualizar o status de um CBSD", async function () {
    await sasSharedRegistry.registerCBSD(
      this.defaultId,
      this.defaultAddress,
      this.defaultGrant,
      this.defaultFreq,
      this.defaultBw,
      this.defaultExpiry
    );
    await expect(sasSharedRegistry.updateStatus(this.defaultId, "active"))
      .to.emit(sasSharedRegistry, "StatusUpdated")
      .withArgs(this.defaultId, "active", owner.address);
    const info = await sasSharedRegistry.getCBSDInfo(this.defaultId);
    expect(info[2]).to.equal("active");
  });

  it("não deve permitir atualizar status de CBSD inexistente", async function () {
    await expect(
      sasSharedRegistry.updateStatus(99, "inactive")
    ).to.be.revertedWith("CBSD not registered");
  });

  it("não deve permitir atualização de status por não-owner", async function () {
    await sasSharedRegistry.registerCBSD(
      this.defaultId,
      this.defaultAddress,
      this.defaultGrant,
      this.defaultFreq,
      this.defaultBw,
      this.defaultExpiry
    );
    await expect(
      sasSharedRegistry.connect(other).updateStatus(this.defaultId, "inactive")
    ).to.be.revertedWith("Not an authorized SAS");
  });
}); 