const { expect } = require("chai");
const { ethers } = require("hardhat");
const { keccak256, solidityPacked } = require("ethers");

// Função utilitária para gerar a chave do CBSD igual ao contrato
function generateCBSDKey(fccId, serialNumber) {
  return keccak256(
    solidityPacked(["string", "string"], [fccId, serialNumber])
  );
}

describe("SASSharedRegistry", function () {
  let SASSharedRegistry, sasSharedRegistry, owner, sas1, sas2, user1;

  beforeEach(async function () {
    [owner, sas1, sas2, user1] = await ethers.getSigners();
    SASSharedRegistry = await ethers.getContractFactory("SASSharedRegistry");
    sasSharedRegistry = await SASSharedRegistry.deploy();
    
    // Autorizar SAS
    await sasSharedRegistry.authorizeSAS(sas1.address);
    await sasSharedRegistry.authorizeSAS(sas2.address);
    
    // Injetar FCC IDs e User IDs válidos
    await sasSharedRegistry.InjectFccId("FCC001", 47);
    await sasSharedRegistry.InjectFccId("FCC002", 47);
    await sasSharedRegistry.InjectUserId("USER001");
    await sasSharedRegistry.InjectUserId("USER002");
    
    // Dados padrão para testes
    this.defaultRegistrationRequest = {
      fccId: "FCC001",
      userId: "USER001",
      cbsdSerialNumber: "SERIAL001",
      callSign: "CALL001",
      cbsdCategory: "A",
      airInterface: "E_UTRA",
      measCapability: ["EUTRA_CARRIER_RSSI"],
      eirpCapability: 47,
      latitude: -23000000, // -23.0 graus em micrograus (exemplo SP)
      longitude: -43000000, // -43.0 graus em micrograus (exemplo RJ)
      height: 30,
      heightType: "AGL",
      indoorDeployment: false,
      antennaGain: 15,
      antennaBeamwidth: 65,
      antennaAzimuth: 180,
      groupingParam: "GROUP1",
      cbsdAddress: "192.168.0.1" // Exemplo de endereço de rede
    };
    
    this.defaultGrantRequest = {
      fccId: "FCC001",
      cbsdSerialNumber: "SERIAL001",
      channelType: "GAA",
      maxEirp: 30,
      lowFrequency: 3550000000, // 3.55 GHz
      highFrequency: 3700000000, // 3.7 GHz
      requestedMaxEirp: 30,
      requestedLowFrequency: 3550000000,
      requestedHighFrequency: 3700000000,
      grantExpireTime: Math.floor(Date.now() / 1000) + 3600 // agora uint, não string
    };
  });

  describe("Configuração Inicial", function () {
    it("deve definir o owner corretamente", async function () {
      expect(await sasSharedRegistry.owner()).to.equal(owner.address);
    });

    it("deve autorizar o owner como SAS inicialmente", async function () {
      expect(await sasSharedRegistry.authorizedSAS(owner.address)).to.be.true;
    });

    it("deve ter contadores zerados inicialmente", async function () {
      expect(await sasSharedRegistry.totalCbsds()).to.equal(0);
      expect(await sasSharedRegistry.totalGrants()).to.equal(0);
    });
  });

  describe("Autorização SAS", function () {
    it("deve permitir owner autorizar SAS", async function () {
      await expect(sasSharedRegistry.authorizeSAS(sas1.address))
        .to.emit(sasSharedRegistry, "SASAuthorized")
        .withArgs(sas1.address);
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
        .to.emit(sasSharedRegistry, "SASRevoked")
        .withArgs(sas1.address);
      expect(await sasSharedRegistry.authorizedSAS(sas1.address)).to.be.false;
    });
  });

  describe("Injeção de IDs", function () {
    it("deve permitir owner injetar FCC ID", async function () {
      const fccId = "FCC003";
      await expect(sasSharedRegistry.InjectFccId(fccId, 47))
        .to.emit(sasSharedRegistry, "FCCIdInjected")
        .withArgs(fccId, 47);
      expect(await sasSharedRegistry.fccIds(fccId)).to.be.true;
    });

    it("deve permitir owner injetar User ID", async function () {
      const userId = "USER003";
      await expect(sasSharedRegistry.InjectUserId(userId))
        .to.emit(sasSharedRegistry, "UserIdInjected")
        .withArgs(userId);
      expect(await sasSharedRegistry.userIds(userId)).to.be.true;
    });
  });

  describe("Registration", function () {
    it("deve registrar um novo CBSD", async function () {
      await expect(sasSharedRegistry.connect(sas1).Registration(this.defaultRegistrationRequest))
        .to.emit(sasSharedRegistry, "CBSDRegistered")
        .withArgs(this.defaultRegistrationRequest.fccId, this.defaultRegistrationRequest.cbsdSerialNumber, sas1.address);
      
      expect(await sasSharedRegistry.totalCbsds()).to.equal(1);
      
      // Verificar dados do CBSD
      const cbsdKey = generateCBSDKey(this.defaultRegistrationRequest.fccId, this.defaultRegistrationRequest.cbsdSerialNumber);
      const cbsd = await sasSharedRegistry.cbsds(cbsdKey);
      expect(cbsd.fccId).to.equal(this.defaultRegistrationRequest.fccId);
      expect(cbsd.userId).to.equal(this.defaultRegistrationRequest.userId);
      expect(cbsd.cbsdAddress).to.equal(this.defaultRegistrationRequest.cbsdAddress);
      expect(cbsd.sasOrigin).to.equal(sas1.address);
    });

    it("deve registrar um novo CBSD com latitude/longitude negativos", async function () {
      await expect(sasSharedRegistry.connect(sas1).Registration(this.defaultRegistrationRequest))
        .to.emit(sasSharedRegistry, "CBSDRegistered")
        .withArgs(this.defaultRegistrationRequest.fccId, this.defaultRegistrationRequest.cbsdSerialNumber, sas1.address);
      
      expect(await sasSharedRegistry.totalCbsds()).to.equal(1);
      
      // Verificar dados do CBSD
      const cbsd = await sasSharedRegistry.getCBSDInfo(this.defaultRegistrationRequest.fccId, this.defaultRegistrationRequest.cbsdSerialNumber);
      expect(cbsd.latitude).to.equal(this.defaultRegistrationRequest.latitude);
      expect(cbsd.longitude).to.equal(this.defaultRegistrationRequest.longitude);
    });

    it("deve registrar um novo CBSD com latitude/longitude positivos", async function () {
      const positiveRequest = { ...this.defaultRegistrationRequest, latitude: 40000000, longitude: 74000000 };
      await expect(sasSharedRegistry.connect(sas1).Registration(positiveRequest))
        .to.emit(sasSharedRegistry, "CBSDRegistered")
        .withArgs(positiveRequest.fccId, positiveRequest.cbsdSerialNumber, sas1.address);
      const cbsd = await sasSharedRegistry.getCBSDInfo(positiveRequest.fccId, positiveRequest.cbsdSerialNumber);
      expect(cbsd.latitude).to.equal(positiveRequest.latitude);
      expect(cbsd.longitude).to.equal(positiveRequest.longitude);
    });

    it("não deve permitir registrar CBSD já registrado", async function () {
      await sasSharedRegistry.connect(sas1).Registration(this.defaultRegistrationRequest);
      await expect(
        sasSharedRegistry.connect(sas1).Registration(this.defaultRegistrationRequest)
      ).to.be.revertedWith("CBSD already exists");
    });

    it("não deve permitir registro com FCC ID não autorizado", async function () {
      const invalidRequest = { ...this.defaultRegistrationRequest };
      invalidRequest.fccId = "INVALID";
      await expect(
        sasSharedRegistry.connect(sas1).Registration(invalidRequest)
      ).to.be.revertedWith("FCC ID not authorized");
    });

    it("não deve permitir registro com User ID não autorizado", async function () {
      const invalidRequest = { ...this.defaultRegistrationRequest };
      invalidRequest.userId = "INVALID";
      await expect(
        sasSharedRegistry.connect(sas1).Registration(invalidRequest)
      ).to.be.revertedWith("User ID not authorized");
    });

    it("não deve permitir registro por SAS não autorizado", async function () {
      await expect(
        sasSharedRegistry.connect(user1).Registration(this.defaultRegistrationRequest)
      ).to.be.revertedWith("Not an authorized SAS");
    });
  });

  describe("GrantSpectrum", function () {
    beforeEach(async function () {
      await sasSharedRegistry.connect(sas1).Registration(this.defaultRegistrationRequest);
    });

    it("deve criar um novo grant", async function () {
      await expect(sasSharedRegistry.connect(sas1).GrantSpectrum(this.defaultGrantRequest))
        .to.emit(sasSharedRegistry, "GrantCreated");
      
      expect(await sasSharedRegistry.totalGrants()).to.equal(1);
      
      // Verificar dados do grant
      const cbsdKey = generateCBSDKey(this.defaultGrantRequest.fccId, this.defaultGrantRequest.cbsdSerialNumber);
      const grants = await sasSharedRegistry.getGrants(this.defaultGrantRequest.fccId, this.defaultGrantRequest.cbsdSerialNumber);
      expect(grants.length).to.equal(1);
      expect(grants[0].maxEirp).to.equal(this.defaultGrantRequest.maxEirp);
      expect(grants[0].lowFrequency).to.equal(this.defaultGrantRequest.lowFrequency);
      expect(grants[0].highFrequency).to.equal(this.defaultGrantRequest.highFrequency);
      expect(grants[0].terminated).to.be.false;
    });

    it("não deve permitir grant para CBSD não registrado", async function () {
      const invalidRequest = { ...this.defaultGrantRequest };
      invalidRequest.cbsdSerialNumber = "INVALID";
      await expect(
        sasSharedRegistry.connect(sas1).GrantSpectrum(invalidRequest)
      ).to.be.revertedWith("CBSD not registered");
    });
  });

  describe("Heartbeat", function () {
    let grantId;

    beforeEach(async function () {
      await sasSharedRegistry.connect(sas1).Registration(this.defaultRegistrationRequest);
      await sasSharedRegistry.connect(sas1).GrantSpectrum(this.defaultGrantRequest);
      
      // Obter o grant ID gerado
      const grants = await sasSharedRegistry.getGrants(this.defaultGrantRequest.fccId, this.defaultGrantRequest.cbsdSerialNumber);
      grantId = grants[0].grantId;
    });

    it("deve aceitar heartbeat válido", async function () {
      await expect(
        sasSharedRegistry.connect(sas1).Heartbeat(
          this.defaultGrantRequest.fccId,
          this.defaultGrantRequest.cbsdSerialNumber,
          grantId
        )
      ).to.not.be.reverted;
    });

    it("não deve aceitar heartbeat para grant inexistente", async function () {
      const invalidGrantId = "INVALID";
      await expect(
        sasSharedRegistry.connect(sas1).Heartbeat(
          this.defaultGrantRequest.fccId,
          this.defaultGrantRequest.cbsdSerialNumber,
          invalidGrantId
        )
      ).to.be.revertedWith("Grant not found");
    });

    it("não deve aceitar heartbeat para CBSD não registrado", async function () {
      await expect(
        sasSharedRegistry.connect(sas1).Heartbeat(
          this.defaultGrantRequest.fccId,
          "INVALID",
          grantId
        )
      ).to.be.revertedWith("CBSD not registered");
    });
  });

  describe("Relinquishment", function () {
    let grantId;

    beforeEach(async function () {
      await sasSharedRegistry.connect(sas1).Registration(this.defaultRegistrationRequest);
      await sasSharedRegistry.connect(sas1).GrantSpectrum(this.defaultGrantRequest);
      
      const grants = await sasSharedRegistry.getGrants(this.defaultGrantRequest.fccId, this.defaultGrantRequest.cbsdSerialNumber);
      grantId = grants[0].grantId;
    });

    it("deve terminar um grant", async function () {
      await expect(
        sasSharedRegistry.connect(sas1).Relinquishment(
          this.defaultGrantRequest.fccId,
          this.defaultGrantRequest.cbsdSerialNumber,
          grantId
        )
      ).to.emit(sasSharedRegistry, "GrantTerminated")
        .withArgs(this.defaultGrantRequest.fccId, this.defaultGrantRequest.cbsdSerialNumber, grantId, sas1.address);
      
      // Verificar se grant foi marcado como terminado
      const grants = await sasSharedRegistry.getGrants(this.defaultGrantRequest.fccId, this.defaultGrantRequest.cbsdSerialNumber);
      expect(grants[0].terminated).to.be.true;
    });
  });

  describe("Deregistration", function () {
    beforeEach(async function () {
      await sasSharedRegistry.connect(sas1).Registration(this.defaultRegistrationRequest);
      await sasSharedRegistry.connect(sas1).GrantSpectrum(this.defaultGrantRequest);
    });

    it("deve remover registro do CBSD", async function () {
      expect(await sasSharedRegistry.totalCbsds()).to.equal(1);
      expect(await sasSharedRegistry.totalGrants()).to.equal(1);
      
      await sasSharedRegistry.connect(sas1).Deregistration(
        this.defaultRegistrationRequest.fccId,
        this.defaultRegistrationRequest.cbsdSerialNumber
      );
      
      expect(await sasSharedRegistry.totalCbsds()).to.equal(0);
      
      // Verificar se CBSD foi removido
      const cbsdKey = generateCBSDKey(this.defaultRegistrationRequest.fccId, this.defaultRegistrationRequest.cbsdSerialNumber);
      const cbsd = await sasSharedRegistry.cbsds(cbsdKey);
      expect(cbsd.fccId).to.equal("");
    });

    it("não deve permitir deregistration de CBSD inexistente", async function () {
      await expect(
        sasSharedRegistry.connect(sas1).Deregistration(
          this.defaultRegistrationRequest.fccId,
          "INVALID"
        )
      ).to.be.revertedWith("CBSD not registered");
    });
  });

  describe("Blacklist", function () {
    it("deve permitir owner blacklistar FCC ID", async function () {
      const fccId = "FCC003";
      await expect(sasSharedRegistry.BlacklistByFccId(fccId))
        .to.emit(sasSharedRegistry, "FCCIdBlacklisted")
        .withArgs(fccId);
      expect(await sasSharedRegistry.blacklistedFccIds(fccId)).to.be.true;
    });

    it("deve permitir owner blacklistar Serial Number", async function () {
      const fccId = "FCC003";
      const serialNumber = "SERIAL003";
      await expect(sasSharedRegistry.BlacklistByFccIdAndSerialNumber(fccId, serialNumber))
        .to.emit(sasSharedRegistry, "SerialNumberBlacklisted")
        .withArgs(fccId, serialNumber);
      const serialKey = generateCBSDKey(fccId, serialNumber);
      expect(await sasSharedRegistry.blacklistedSerialNumbers(serialKey)).to.be.true;
    });
  });

  describe("Reset", function () {
    beforeEach(async function () {
      await sasSharedRegistry.connect(sas1).Registration(this.defaultRegistrationRequest);
      await sasSharedRegistry.connect(sas1).GrantSpectrum(this.defaultGrantRequest);
    });

    it("deve permitir owner resetar o SAS", async function () {
      expect(await sasSharedRegistry.totalCbsds()).to.equal(1);
      expect(await sasSharedRegistry.totalGrants()).to.equal(1);
      
      await sasSharedRegistry.Reset();
      
      expect(await sasSharedRegistry.totalCbsds()).to.equal(0);
      expect(await sasSharedRegistry.totalGrants()).to.equal(0);
    });

    it("não deve permitir não-owner resetar o SAS", async function () {
      await expect(
        sasSharedRegistry.connect(user1).Reset()
      ).to.be.revertedWith("Not authorized");
    });
  });
}); 