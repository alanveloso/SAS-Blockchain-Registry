const { expect } = require("chai");
const { ethers } = require("hardhat");
const { anyValue } = require("@nomicfoundation/hardhat-chai-matchers/withArgs");

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
    // Exemplo de dados para RegistrationRequest
    const registrationRequest = {
      fccId: "FCC123",
      userId: "USR1",
      cbsdSerialNumber: "SN123",
      callSign: "CALL1",
      cbsdCategory: "A",
      airInterface: "E-UTRA",
      measCapability: ["RECEIVED_POWER_WITHOUT_GRANT"],
      eirpCapability: 30,
      latitude: 12345,
      longitude: 67890,
      height: 10,
      heightType: "AGL",
      indoorDeployment: true,
      antennaGain: 5,
      antennaBeamwidth: 60,
      antennaAzimuth: 90,
      groupingParam: "group1",
      cbsdAddress: "192.168.0.1"
    };
    // Exemplo de dados para GrantRequest
    const grantRequest = {
      fccId: "FCC123",
      cbsdSerialNumber: "SN123",
      channelType: "GAA",
      maxEirp: 30,
      lowFrequency: 3550000000,
      highFrequency: 3570000000,
      requestedMaxEirp: 30,
      requestedLowFrequency: 3550000000,
      requestedHighFrequency: 3570000000,
      grantExpireTime: 2000000000
    };

    it("deve registrar um CBSD e emitir evento CBSDRegistered", async function () {
      await expect(sasSharedRegistry.connect(sas1).registration(registrationRequest))
        .to.emit(sasSharedRegistry, "CBSDRegistered")
        .withArgs(
          registrationRequest.fccId,
          registrationRequest.cbsdSerialNumber,
          sas1.address
        );
    });

    it("deve criar um grant e emitir evento GrantCreated", async function () {
      await sasSharedRegistry.connect(sas1).registration(registrationRequest);
      await expect(sasSharedRegistry.connect(sas1).grant(grantRequest))
        .to.emit(sasSharedRegistry, "GrantCreated")
        .withArgs(
          grantRequest.fccId,
          grantRequest.cbsdSerialNumber,
          anyValue,
          sas1.address
        );
    });

    it("deve terminar um grant e emitir evento GrantTerminated", async function () {
      await sasSharedRegistry.connect(sas1).registration(registrationRequest);
      // Executa a transação de grant e aguarda o receipt
      const tx = await sasSharedRegistry.connect(sas1).grant(grantRequest);
      const receipt = await tx.wait();
      // Decodifica o evento GrantCreated manualmente
      const iface = sasSharedRegistry.interface;
      let grantId;
      for (const log of receipt.logs) {
        try {
          const parsed = iface.parseLog(log);
          if (parsed.name === "GrantCreated") {
            grantId = parsed.args.grantId;
            break;
          }
        } catch (e) {}
      }
      expect(grantId).to.not.be.undefined;
      await expect(
        sasSharedRegistry.connect(sas1).relinquishment(grantRequest.fccId, grantRequest.cbsdSerialNumber, grantId)
      ).to.emit(sasSharedRegistry, "GrantTerminated");
    });

    it("deve permitir deregistration de CBSD", async function () {
      await sasSharedRegistry.connect(sas1).registration(registrationRequest);
      await expect(
        sasSharedRegistry.connect(sas1).deregistration(registrationRequest.fccId, registrationRequest.cbsdSerialNumber)
      ).not.to.be.reverted;
    });

    it("não deve permitir chamada por SAS não autorizado", async function () {
      await expect(
        sasSharedRegistry.connect(user1).registration(registrationRequest)
      ).to.be.revertedWith("Not an authorized SAS");
      await expect(
        sasSharedRegistry.connect(user1).grant(grantRequest)
      ).to.be.revertedWith("Not an authorized SAS");
      await expect(
        sasSharedRegistry.connect(user1).relinquishment(grantRequest.fccId, grantRequest.cbsdSerialNumber, "grantId")
      ).to.be.revertedWith("Not an authorized SAS");
      await expect(
        sasSharedRegistry.connect(user1).deregistration(registrationRequest.fccId, registrationRequest.cbsdSerialNumber)
      ).to.be.revertedWith("Not an authorized SAS");
    });
  });
}); 