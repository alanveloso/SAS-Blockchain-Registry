const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("SASSharedRegistry (Simplificado)", function () {
  let SASSharedRegistry, sasSharedRegistry, owner, sas1, sas2, user1;

  beforeEach(async function () {
    [owner, sas1, sas2, user1] = await ethers.getSigners();
    SASSharedRegistry = await ethers.getContractFactory("SASSharedRegistry");
    sasSharedRegistry = await SASSharedRegistry.deploy();
    await sasSharedRegistry.authorizeSAS(sas1.address);
    await sasSharedRegistry.authorizeSAS(sas2.address);
  });

  describe("Autorização SAS", function () {
    it("deve permitir owner autorizar SAS", async function () {
      await expect(sasSharedRegistry.authorizeSAS(sas1.address))
        .to.emit(sasSharedRegistry, "SASAuthorized");
      expect(await sasSharedRegistry.authorizedSAS(sas1.address)).to.be.true;
    });

    it("não deve permitir não-owner autorizar SAS", async function () {
      await expect(
        sasSharedRegistry.connect(user1).authorizeSAS(sas1.address)
      ).to.be.revertedWith("Not authorized");
    });

    it("deve permitir owner revogar SAS", async function () {
      await sasSharedRegistry.authorizeSAS(sas1.address);
      await expect(sasSharedRegistry.revokeSAS(sas1.address))
        .to.emit(sasSharedRegistry, "SASRevoked");
      expect(await sasSharedRegistry.authorizedSAS(sas1.address)).to.be.false;
    });
  });

  describe("Funções SAS-SAS", function () {
    const payload = '{"example": "data"}';

    it("deve emitir evento Registration", async function () {
      await expect(sasSharedRegistry.connect(sas1).registration(payload))
        .to.emit(sasSharedRegistry, "Registration");
    });

    it("deve emitir evento Grant", async function () {
      await expect(sasSharedRegistry.connect(sas1).grant(payload))
        .to.emit(sasSharedRegistry, "Grant");
    });

    it("deve emitir evento Heartbeat", async function () {
      await expect(sasSharedRegistry.connect(sas1).heartbeat(payload))
        .to.emit(sasSharedRegistry, "Heartbeat");
    });

    it("deve emitir evento Relinquishment", async function () {
      await expect(sasSharedRegistry.connect(sas1).relinquishment(payload))
        .to.emit(sasSharedRegistry, "Relinquishment");
    });

    it("deve emitir evento Deregistration", async function () {
      await expect(sasSharedRegistry.connect(sas1).deregistration(payload))
        .to.emit(sasSharedRegistry, "Deregistration");
    });

    it("não deve permitir chamada por SAS não autorizado", async function () {
      await expect(
        sasSharedRegistry.connect(user1).registration(payload)
      ).to.be.revertedWith("Not an authorized SAS");
      await expect(
        sasSharedRegistry.connect(user1).grant(payload)
      ).to.be.revertedWith("Not an authorized SAS");
      await expect(
        sasSharedRegistry.connect(user1).heartbeat(payload)
      ).to.be.revertedWith("Not an authorized SAS");
      await expect(
        sasSharedRegistry.connect(user1).relinquishment(payload)
      ).to.be.revertedWith("Not an authorized SAS");
      await expect(
        sasSharedRegistry.connect(user1).deregistration(payload)
      ).to.be.revertedWith("Not an authorized SAS");
    });
  });
}); 