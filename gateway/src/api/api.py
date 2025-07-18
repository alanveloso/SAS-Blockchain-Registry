from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
import logging
from blockchain.blockchain import Blockchain
from repository.repository import CBSDRepository
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
    description="API REST para comunicação SAS-SAS via blockchain",
    version="3.0.0"
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

# Modelos Pydantic para SAS-SAS
class RegistrationRequest(BaseModel):
    fccId: str
    userId: str
    cbsdSerialNumber: str
    callSign: str
    cbsdCategory: str
    airInterface: str
    measCapability: List[str]
    eirpCapability: int
    latitude: int
    longitude: int
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
    transmitExpireTime: Optional[int] = None

class RelinquishmentRequest(BaseModel):
    fccId: str
    cbsdSerialNumber: str
    grantId: str

class DeregistrationRequest(BaseModel):
    fccId: str
    cbsdSerialNumber: str

class SASAuthorization(BaseModel):
    sas_address: str

class RegistrationRequestWithKey(RegistrationRequest):
    private_key: str = None
class GrantRequestWithKey(GrantRequest):
    private_key: str = None
class RelinquishmentRequestWithKey(RelinquishmentRequest):
    private_key: str = None
class DeregistrationRequestWithKey(DeregistrationRequest):
    private_key: str = None

class SASAuthorizationWithKey(SASAuthorization):
    private_key: str = None

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
        "message": "SAS Shared Registry API (SAS-SAS)",
        "version": "3.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check da API"""
    try:
        if blockchain:
            latest_block = blockchain.get_latest_block()
            owner = blockchain.get_owner()
            return {
                "status": "healthy",
                "blockchain_connected": True,
                "latest_block": latest_block,
                "contract_address": blockchain.contract.address,
                "owner": owner
            }
        else:
            return {"status": "unhealthy", "blockchain_connected": False}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Endpoints SAS-SAS

@app.post("/v1.3/registration")
async def registration(req: RegistrationRequestWithKey):
    """Registration - Registra um CBSD via SAS-SAS"""
    try:
        blockchain = Blockchain(req.private_key)
        receipt = blockchain.registration(req.dict(exclude={"private_key"}))
        return {
            "success": True,
            "message": f"CBSD {req.fccId}/{req.cbsdSerialNumber} registrado via SAS-SAS",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro no registro SAS-SAS: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1.3/grant")
async def grant_spectrum(req: GrantRequestWithKey):
    """Grant - Solicita espectro via SAS-SAS"""
    try:
        blockchain = Blockchain(req.private_key)
        receipt = blockchain.grant(req.dict(exclude={"private_key"}))
        return {
            "success": True,
            "message": f"Grant solicitado para {req.fccId}/{req.cbsdSerialNumber} via SAS-SAS",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro no grant SAS-SAS: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1.3/relinquishment")
async def relinquishment(req: RelinquishmentRequestWithKey):
    """Relinquishment - Libera grant via SAS-SAS"""
    try:
        blockchain = Blockchain(req.private_key)
        receipt = blockchain.relinquishment(req.dict(exclude={"private_key"}))
        return {
            "success": True,
            "message": f"Relinquishment executado para {req.fccId}/{req.cbsdSerialNumber} via SAS-SAS",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro no relinquishment SAS-SAS: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1.3/deregistration")
async def deregistration(req: DeregistrationRequestWithKey):
    """Deregistration - Remove CBSD via SAS-SAS"""
    try:
        blockchain = Blockchain(req.private_key)
        receipt = blockchain.deregistration(req.dict(exclude={"private_key"}))
        return {
            "success": True,
            "message": f"Deregistration executado para {req.fccId}/{req.cbsdSerialNumber} via SAS-SAS",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro no deregistration SAS-SAS: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Endpoints de autorização SAS

@app.get("/sas/{sas_address}/authorized")
async def check_sas_authorization(sas_address: str):
    """Verifica se um endereço é um SAS autorizado"""
    try:
        is_authorized = blockchain.is_authorized_sas(sas_address)
        return {
            "sas_address": sas_address,
            "authorized": is_authorized
        }
    except Exception as e:
        logger.error(f"Erro ao verificar autorização SAS: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/sas/authorize")
async def authorize_sas(req: SASAuthorizationWithKey):
    try:
        blockchain = Blockchain(req.private_key)
        receipt = blockchain.authorize_sas(req.sas_address)
        return {
            "success": True,
            "message": f"SAS {req.sas_address} autorizado",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro ao autorizar SAS: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/sas/revoke")
async def revoke_sas(req: SASAuthorizationWithKey):
    try:
        blockchain = Blockchain(req.private_key)
        receipt = blockchain.revoke_sas(req.sas_address)
        return {
            "success": True,
            "message": f"SAS {req.sas_address} revogado",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro ao revogar SAS: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Endpoints de informações

@app.get("/stats")
async def get_stats():
    """Obtém estatísticas do contrato"""
    try:
        owner = blockchain.get_owner()
        latest_block = blockchain.get_latest_block()
        return {
            "owner": owner,
            "contract_address": blockchain.contract.address,
            "latest_block": latest_block,
            "version": "3.0.0 (SAS-SAS)"
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/events/recent")
async def get_recent_events():
    """Obtém eventos recentes do contrato"""
    try:
        # Obter eventos dos últimos 10 blocos
        from_block = blockchain.get_latest_block() - 10
        
        events = []
        
        # Eventos SAS-SAS (têm sasOrigin, grantId, registrationTimestamp/grantTimestamp)
        for event_name in ['CBSDRegistered', 'GrantCreated', 'GrantTerminated']:
            try:
                event_filter = blockchain.get_event_filter(event_name, from_block)
                event_entries = event_filter.get_all_entries()

                for event in event_entries:
                    try:
                        decoded_logs = blockchain.contract.events[event_name].process_log(event)
                        event_data = {
                            "event": event_name,
                            "block_number": int(event['blockNumber']),
                            "transaction_hash": event['transactionHash'].hex() if isinstance(event['transactionHash'], bytes) else str(event['transactionHash']),
                        }
                        # Campos específicos por evento
                        if event_name == 'CBSDRegistered':
                            event_data["sasOrigin"] = str(decoded_logs['args']['sasOrigin'])
                            event_data["fccId"] = str(decoded_logs['args']['fccId'])
                            event_data["serialNumber"] = str(decoded_logs['args']['serialNumber'])
                            event_data["timestamp"] = int(event['blockNumber'])
                        elif event_name == 'GrantCreated':
                            event_data["sasOrigin"] = str(decoded_logs['args']['sasOrigin'])
                            event_data["fccId"] = str(decoded_logs['args']['fccId'])
                            event_data["serialNumber"] = str(decoded_logs['args']['serialNumber'])
                            event_data["grantId"] = str(decoded_logs['args']['grantId'])
                            event_data["timestamp"] = int(event['blockNumber'])
                        elif event_name == 'GrantTerminated':
                            event_data["sasOrigin"] = str(decoded_logs['args']['sasOrigin'])
                            event_data["fccId"] = str(decoded_logs['args']['fccId'])
                            event_data["serialNumber"] = str(decoded_logs['args']['serialNumber'])
                            event_data["grantId"] = str(decoded_logs['args']['grantId'])
                            event_data["timestamp"] = int(event['blockNumber'])
                        events.append(event_data)
                    except Exception as decode_error:
                        logger.warning(f"Erro ao decodificar evento {event_name}: {decode_error}")
                        continue
            except Exception as e:
                logger.warning(f"Erro ao obter eventos {event_name}: {e}")
        
        # Eventos de autorização SAS (têm apenas sas)
        for event_name in ['SASAuthorized', 'SASRevoked']:
            try:
                event_filter = blockchain.get_event_filter(event_name, from_block)
                event_entries = event_filter.get_all_entries()
                
                for event in event_entries:
                    try:
                        # Decodificar os logs do evento
                        decoded_logs = blockchain.contract.events[event_name].process_log(event)
                        events.append({
                            "event": event_name,
                            "block_number": int(event['blockNumber']),
                            "transaction_hash": event['transactionHash'].hex() if isinstance(event['transactionHash'], bytes) else str(event['transactionHash']),
                            "sas": decoded_logs['args']['sas']
                        })
                    except Exception as decode_error:
                        logger.warning(f"Erro ao decodificar evento {event_name}: {decode_error}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Erro ao obter eventos {event_name}: {e}")
        
        # Ordenar por bloco
        events.sort(key=lambda x: x['block_number'], reverse=True)
        
        return {
            "events": events[:50],  # Limitar a 50 eventos
            "total": len(events)
        }
    except Exception as e:
        logger.error(f"Erro ao obter eventos recentes: {e}")
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 