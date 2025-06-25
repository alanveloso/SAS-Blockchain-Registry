from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
import logging
from src.blockchain.blockchain import Blockchain
from src.repository.repository import CBSDRepository
import asyncio
import json
from web3 import Web3
from datetime import datetime, timezone

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="SAS Shared Registry API",
    description="API REST para comunicação SAS-SAS via blockchain (WinnForum)",
    version="2.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instâncias globais
blockchain = None
repo = CBSDRepository()

# Modelos Pydantic para WinnForum
class RegistrationRequest(BaseModel):
    fccId: str
    userId: str
    cbsdSerialNumber: str
    callSign: str
    cbsdCategory: str
    airInterface: str
    measCapability: List[str]
    eirpCapability: int
    latitude: int  # int256 para aceitar valores negativos
    longitude: int  # int256 para aceitar valores negativos
    height: int
    heightType: str
    indoorDeployment: bool
    antennaGain: int
    antennaBeamwidth: int
    antennaAzimuth: int
    groupingParam: str
    cbsdAddress: str

class GrantRequest(BaseModel):
    fccId: str
    cbsdSerialNumber: str
    channelType: str
    maxEirp: int
    lowFrequency: int
    highFrequency: int
    requestedMaxEirp: int
    requestedLowFrequency: int
    requestedHighFrequency: int
    grantExpireTime: int

class HeartbeatRequest(BaseModel):
    fccId: str
    cbsdSerialNumber: str
    grantId: str

class RelinquishmentRequest(BaseModel):
    fccId: str
    cbsdSerialNumber: str
    grantId: str

class DeregistrationRequest(BaseModel):
    fccId: str
    cbsdSerialNumber: str

class SASAuthorization(BaseModel):
    sas_address: str

class FCCIdInjection(BaseModel):
    fccId: str
    maxEirp: int = 47

class UserIdInjection(BaseModel):
    userId: str

class BlacklistRequest(BaseModel):
    fccId: str
    serialNumber: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Inicializar blockchain na startup"""
    global blockchain
    try:
        blockchain = Blockchain()
        logger.info("API iniciada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar blockchain: {e}")
        raise

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "SAS Shared Registry API (WinnForum)",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check da API"""
    try:
        if blockchain:
            latest_block = blockchain.get_latest_block()
            total_cbsds = blockchain.get_total_cbsds()
            total_grants = blockchain.get_total_grants()
            return {
                "status": "healthy",
                "blockchain_connected": True,
                "latest_block": latest_block,
                "contract_address": blockchain.contract.address,
                "total_cbsds": total_cbsds,
                "total_grants": total_grants
            }
        else:
            return {"status": "unhealthy", "blockchain_connected": False}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Endpoints SAS-SAS (WinnForum)

@app.post("/v1.3/registration")
async def registration(reg_request: RegistrationRequest):
    """Registration - Registra um CBSD"""
    try:
        # Parâmetros já são string, passar diretamente
        registration_params = (
            reg_request.fccId,                    # fccId
            reg_request.userId,                   # userId
            reg_request.cbsdSerialNumber,         # cbsdSerialNumber
            reg_request.callSign,                 # callSign
            reg_request.cbsdCategory,             # cbsdCategory
            reg_request.airInterface,             # airInterface
            reg_request.measCapability,           # measCapability (list of str)
            reg_request.eirpCapability,           # eirpCapability
            reg_request.latitude,                 # latitude
            reg_request.longitude,                # longitude
            reg_request.height,                   # height
            reg_request.heightType,               # heightType
            reg_request.indoorDeployment,         # indoorDeployment
            reg_request.antennaGain,              # antennaGain
            reg_request.antennaBeamwidth,         # antennaBeamwidth
            reg_request.antennaAzimuth,           # antennaAzimuth
            reg_request.groupingParam,            # groupingParam
            reg_request.cbsdAddress               # cbsdAddress
        )
        tx = blockchain.contract.functions.Registration(registration_params)
        receipt = blockchain.send_transaction(tx)
        return {
            "success": True,
            "message": f"CBSD {reg_request.fccId}/{reg_request.cbsdSerialNumber} registrado",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro no registro: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1.3/grant")
async def grant_spectrum(grant_request: GrantRequest):
    """Grant - Solicita espectro"""
    try:
        grant_params = (
            grant_request.fccId,                    # fccId
            grant_request.cbsdSerialNumber,         # cbsdSerialNumber
            grant_request.channelType,              # channelType
            grant_request.maxEirp,                  # maxEirp
            grant_request.lowFrequency,             # lowFrequency
            grant_request.highFrequency,            # highFrequency
            grant_request.requestedMaxEirp,         # requestedMaxEirp
            grant_request.requestedLowFrequency,    # requestedLowFrequency
            grant_request.requestedHighFrequency,   # requestedHighFrequency
            grant_request.grantExpireTime           # grantExpireTime
        )
        tx = blockchain.contract.functions.GrantSpectrum(grant_params)
        receipt = blockchain.send_transaction(tx)
        return {
            "success": True,
            "message": f"Grant solicitado para {grant_request.fccId}/{grant_request.cbsdSerialNumber}",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro na solicitação de grant: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1.3/heartbeat")
async def heartbeat(heartbeat_request: HeartbeatRequest):
    """Heartbeat - Renova um grant"""
    try:
        tx = blockchain.contract.functions.Heartbeat(
            heartbeat_request.fccId,
            heartbeat_request.cbsdSerialNumber,
            heartbeat_request.grantId
        )
        receipt = blockchain.send_transaction(tx)
        return {
            "success": True,
            "message": f"Heartbeat enviado para grant {heartbeat_request.grantId}",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro no heartbeat: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1.3/relinquishment")
async def relinquishment(relinquishment_request: RelinquishmentRequest):
    """Relinquishment - Relinquishes um grant"""
    try:
        tx = blockchain.contract.functions.Relinquishment(
            relinquishment_request.fccId,
            relinquishment_request.cbsdSerialNumber,
            relinquishment_request.grantId
        )
        receipt = blockchain.send_transaction(tx)
        return {
            "success": True,
            "message": f"Grant {relinquishment_request.grantId} relinquished",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro no relinquishment: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1.3/deregistration")
async def deregistration(dereg_request: DeregistrationRequest):
    """Deregistration - Desregistra um CBSD"""
    try:
        tx = blockchain.contract.functions.Deregistration(
            dereg_request.fccId,
            dereg_request.cbsdSerialNumber
        )
        receipt = blockchain.send_transaction(tx)
        return {
            "success": True,
            "message": f"CBSD {dereg_request.fccId}/{dereg_request.cbsdSerialNumber} desregistrado",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro na desregistração: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Endpoints de consulta

@app.get("/cbsd/{fcc_id}/{serial_number}")
async def get_cbsd_info(fcc_id: str, serial_number: str):
    """Obtém informações completas de um CBSD"""
    try:
        cbsd_info = blockchain.get_cbsd_info(fcc_id, serial_number)
        grants = blockchain.get_grants(fcc_id, serial_number)
        return {
            "success": True,
            "cbsd": {
                "fccId": fcc_id,
                "serialNumber": serial_number,
                "userId": cbsd_info[1],
                "callSign": cbsd_info[3],
                "category": cbsd_info[4],
                "latitude": cbsd_info[8],
                "longitude": cbsd_info[9],
                "height": cbsd_info[10],
                "indoorDeployment": cbsd_info[12],
                "antennaGain": cbsd_info[13],
                "cbsdAddress": cbsd_info[16],
                "sasOrigin": cbsd_info[17],
                "registrationTimestamp": cbsd_info[18]
            },
            "grants": [
                {
                    "grantId": grant[0],
                    "channelType": grant[1],
                    "maxEirp": grant[4],
                    "lowFrequency": grant[5],
                    "highFrequency": grant[6],
                    "terminated": grant[3],
                    "expireTime": grant[2]
                }
                for grant in grants
            ]
        }
    except Exception as e:
        logger.error(f"Erro ao obter info do CBSD: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/cbsd/{fcc_id}/{serial_number}/registered")
async def is_cbsd_registered(fcc_id: str, serial_number: str):
    """Verifica se um CBSD está registrado"""
    try:
        is_registered = blockchain.is_cbsd_registered(fcc_id, serial_number)
        return {
            "success": True,
            "fccId": fcc_id,
            "serialNumber": serial_number,
            "registered": is_registered
        }
    except Exception as e:
        logger.error(f"Erro ao verificar registro: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/sas/{sas_address}/authorized")
async def check_sas_authorization(sas_address: str):
    """Verifica se um endereço é um SAS autorizado"""
    try:
        is_authorized = blockchain.is_authorized_sas(sas_address)
        return {
            "success": True,
            "sas_address": sas_address,
            "authorized": is_authorized
        }
    except Exception as e:
        logger.error(f"Erro ao verificar autorização SAS: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Obtém estatísticas do contrato"""
    try:
        total_cbsds = blockchain.get_total_cbsds()
        total_grants = blockchain.get_total_grants()
        latest_block = blockchain.get_latest_block()
        
        return {
            "success": True,
            "total_cbsds": total_cbsds,
            "total_grants": total_grants,
            "latest_block": latest_block
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Endpoints administrativos (WinnForum)

@app.post("/v1.3/admin/authorize")
async def authorize_sas(sas_auth: SASAuthorization):
    """Autorizar um SAS"""
    try:
        tx = blockchain.contract.functions.authorizeSAS(sas_auth.sas_address)
        receipt = blockchain.send_transaction(tx)
        
        return {
            "success": True,
            "message": f"SAS {sas_auth.sas_address} autorizado",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro ao autorizar SAS: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1.3/admin/revoke")
async def revoke_sas(sas_auth: SASAuthorization):
    """Revogar um SAS"""
    try:
        tx = blockchain.contract.functions.revokeSAS(sas_auth.sas_address)
        receipt = blockchain.send_transaction(tx)
        
        return {
            "success": True,
            "message": f"SAS {sas_auth.sas_address} revogado",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro ao revogar SAS: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1.3/admin/injectFccId")
async def inject_fcc_id(fcc_injection: FCCIdInjection):
    """InjectFccId - Injeta FCC ID válido"""
    try:
        tx = blockchain.contract.functions.InjectFccId(fcc_injection.fccId, fcc_injection.maxEirp)
        receipt = blockchain.send_transaction(tx)
        return {
            "success": True,
            "message": f"FCC ID {fcc_injection.fccId} injetado",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro ao injetar FCC ID: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1.3/admin/injectUserId")
async def inject_user_id(user_injection: UserIdInjection):
    """InjectUserId - Injeta User ID válido"""
    try:
        tx = blockchain.contract.functions.InjectUserId(user_injection.userId)
        receipt = blockchain.send_transaction(tx)
        return {
            "success": True,
            "message": f"User ID {user_injection.userId} injetado",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro ao injetar User ID: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1.3/admin/blacklist")
async def blacklist(blacklist_request: BlacklistRequest):
    """Blacklist - Blacklista FCC ID ou Serial Number"""
    try:
        if blacklist_request.serialNumber:
            tx = blockchain.contract.functions.BlacklistByFccIdAndSerialNumber(
                blacklist_request.fccId,
                blacklist_request.serialNumber
            )
            message = f"Serial number {blacklist_request.serialNumber} blacklistado"
        else:
            tx = blockchain.contract.functions.BlacklistByFccId(blacklist_request.fccId)
            message = f"FCC ID {blacklist_request.fccId} blacklistado"
        receipt = blockchain.send_transaction(tx)
        return {
            "success": True,
            "message": message,
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro ao blacklistar: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1.3/admin/reset")
async def reset():
    """Reset - Reseta o SAS"""
    try:
        tx = blockchain.contract.functions.Reset()
        receipt = blockchain.send_transaction(tx)
        
        return {
            "success": True,
            "message": "SAS resetado",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro ao resetar SAS: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint WinnForum Full Activity Dump
@app.get("/v1.3/dump")
async def get_full_activity_dump():
    """Full Activity Dump - Endpoint WinnForum v1.3"""
    try:
        # Obter dados do blockchain
        total_cbsds = blockchain.get_total_cbsds()
        total_grants = blockchain.get_total_grants()
        
        # Gerar timestamp no formato ISO 8601 (WinnForum)
        generation_datetime = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Estrutura WinnForum v1.3 Full Activity Dump
        dump_data = {
            "version": "1.3",
            "generationDateTime": generation_datetime,
            "cbsdRecords": [],
            "escSensorDataRecords": [],
            "coordinationEventRecords": [],
            "ppaRecords": [],
            "palRecords": [],
            "zoneRecords": [],
            "exclusionZoneRecords": [],
            "fssRecords": [],
            "wispRecords": [],
            "sasAdministratorRecords": []
        }
        
        # TODO: Implementar conversão de dados do blockchain para formato WinnForum
        # Por enquanto, retorna estrutura vazia mas válida
        
        return dump_data
        
    except Exception as e:
        logger.error(f"Erro ao gerar Full Activity Dump: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 