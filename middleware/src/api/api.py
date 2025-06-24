from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import logging
from src.blockchain.blockchain import Blockchain
from src.repository.repository import CBSDRepository
import asyncio
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="SAS Shared Registry API",
    description="API REST para comunicação SAS-SAS via blockchain",
    version="1.0.0"
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

# Modelos Pydantic
class CBSDRegistration(BaseModel):
    cbsd_id: int
    cbsd_address: str
    grant_amount: int
    frequency_hz: int
    bandwidth_hz: int
    expiry_timestamp: int

class SASAuthorization(BaseModel):
    sas_address: str

class GrantUpdate(BaseModel):
    cbsd_id: int
    new_grant_amount: int

class StatusUpdate(BaseModel):
    cbsd_id: int
    new_status: str

class GrantDetailsUpdate(BaseModel):
    cbsd_id: int
    frequency_hz: int
    bandwidth_hz: int
    expiry_timestamp: int

class CBSDInfo(BaseModel):
    cbsd_id: int
    cbsd_address: str
    grant_amount: int
    status: str
    frequency_hz: int
    bandwidth_hz: int
    expiry_timestamp: int
    sas_origin: str

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
        "message": "SAS Shared Registry API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check da API"""
    try:
        if blockchain:
            latest_block = blockchain.get_latest_block()
            return {
                "status": "healthy",
                "blockchain_connected": True,
                "latest_block": latest_block,
                "contract_address": blockchain.contract.address
            }
        else:
            return {"status": "unhealthy", "blockchain_connected": False}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Endpoints SAS-SAS

@app.post("/sas/authorize")
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

@app.post("/sas/revoke")
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

@app.post("/cbsd/register")
async def register_cbsd(cbsd_reg: CBSDRegistration):
    """Registrar um CBSD"""
    try:
        tx = blockchain.contract.functions.registerCBSD(
            cbsd_reg.cbsd_id,
            cbsd_reg.cbsd_address,
            cbsd_reg.grant_amount,
            cbsd_reg.frequency_hz,
            cbsd_reg.bandwidth_hz,
            cbsd_reg.expiry_timestamp
        )
        receipt = blockchain.send_transaction(tx)
        
        # Armazenar no repositório local
        repo.add(cbsd_reg.cbsd_id, {
            'id': cbsd_reg.cbsd_id,
            'cbsd_address': cbsd_reg.cbsd_address,
            'grant_amount': cbsd_reg.grant_amount,
            'status': 'registered',
            'frequency_hz': cbsd_reg.frequency_hz,
            'bandwidth_hz': cbsd_reg.bandwidth_hz,
            'expiry_timestamp': cbsd_reg.expiry_timestamp,
            'block_number': receipt['blockNumber'],
            'transaction_hash': receipt['transactionHash'].hex()
        })
        
        return {
            "success": True,
            "message": f"CBSD {cbsd_reg.cbsd_id} registrado",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro ao registrar CBSD: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/cbsd/grant-amount")
async def update_grant_amount(grant_update: GrantUpdate):
    """Atualizar grant amount de um CBSD"""
    try:
        tx = blockchain.contract.functions.updateGrantAmount(
            grant_update.cbsd_id,
            grant_update.new_grant_amount
        )
        receipt = blockchain.send_transaction(tx)
        
        # Atualizar no repositório local
        cbsd_data = repo.get(grant_update.cbsd_id)
        if cbsd_data:
            cbsd_data['grant_amount'] = grant_update.new_grant_amount
            cbsd_data['last_update'] = receipt['blockNumber']
            repo.add(grant_update.cbsd_id, cbsd_data)
        
        return {
            "success": True,
            "message": f"Grant amount do CBSD {grant_update.cbsd_id} atualizado",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro ao atualizar grant amount: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/cbsd/status")
async def update_status(status_update: StatusUpdate):
    """Atualizar status de um CBSD"""
    try:
        tx = blockchain.contract.functions.updateStatus(
            status_update.cbsd_id,
            status_update.new_status
        )
        receipt = blockchain.send_transaction(tx)
        
        # Atualizar no repositório local
        cbsd_data = repo.get(status_update.cbsd_id)
        if cbsd_data:
            cbsd_data['status'] = status_update.new_status
            cbsd_data['last_update'] = receipt['blockNumber']
            repo.add(status_update.cbsd_id, cbsd_data)
        
        return {
            "success": True,
            "message": f"Status do CBSD {status_update.cbsd_id} atualizado",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro ao atualizar status: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/cbsd/grant-details")
async def update_grant_details(details_update: GrantDetailsUpdate):
    """Atualizar detalhes do grant de um CBSD"""
    try:
        tx = blockchain.contract.functions.updateGrantDetails(
            details_update.cbsd_id,
            details_update.frequency_hz,
            details_update.bandwidth_hz,
            details_update.expiry_timestamp
        )
        receipt = blockchain.send_transaction(tx)
        
        # Atualizar no repositório local
        cbsd_data = repo.get(details_update.cbsd_id)
        if cbsd_data:
            cbsd_data.update({
                'frequency_hz': details_update.frequency_hz,
                'bandwidth_hz': details_update.bandwidth_hz,
                'expiry_timestamp': details_update.expiry_timestamp,
                'last_update': receipt['blockNumber']
            })
            repo.add(details_update.cbsd_id, cbsd_data)
        
        return {
            "success": True,
            "message": f"Detalhes do grant do CBSD {details_update.cbsd_id} atualizados",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro ao atualizar detalhes do grant: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Endpoints de consulta

@app.get("/cbsd/{cbsd_id}")
async def get_cbsd_info(cbsd_id: int):
    """Obter informações de um CBSD"""
    try:
        # Buscar na blockchain
        cbsd_info = blockchain.get_cbsd_info(cbsd_id)
        
        # Buscar no repositório local
        local_data = repo.get(cbsd_id)
        
        return {
            "cbsd_id": cbsd_id,
            "blockchain_data": {
                "cbsd_address": cbsd_info[0],
                "grant_amount": cbsd_info[1],
                "status": cbsd_info[2],
                "frequency_hz": cbsd_info[3],
                "bandwidth_hz": cbsd_info[4],
                "expiry_timestamp": cbsd_info[5],
                "sas_origin": cbsd_info[6]
            },
            "local_data": local_data
        }
    except Exception as e:
        logger.error(f"Erro ao obter info do CBSD {cbsd_id}: {e}")
        raise HTTPException(status_code=404, detail=f"CBSD {cbsd_id} não encontrado")

@app.get("/cbsd")
async def list_cbsds():
    """Listar todos os CBSDs"""
    try:
        cbsds = []
        for cbsd_id, data in repo.cbsds.items():
            cbsds.append({
                "cbsd_id": cbsd_id,
                **data
            })
        
        return {
            "total": len(cbsds),
            "cbsds": cbsds
        }
    except Exception as e:
        logger.error(f"Erro ao listar CBSDs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sas/{sas_address}/authorized")
async def check_sas_authorization(sas_address: str):
    """Verificar se um SAS está autorizado"""
    try:
        is_authorized = blockchain.is_authorized_sas(sas_address)
        return {
            "sas_address": sas_address,
            "authorized": is_authorized
        }
    except Exception as e:
        logger.error(f"Erro ao verificar autorização do SAS {sas_address}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/events/recent")
async def get_recent_events():
    """Obter eventos recentes"""
    try:
        # Retornar eventos do repositório local
        events = []
        for cbsd_id, data in repo.cbsds.items():
            if 'transaction_hash' in data:
                events.append({
                    "cbsd_id": cbsd_id,
                    "event_type": "CBSDRegistered",
                    "transaction_hash": data['transaction_hash'],
                    "block_number": data.get('block_number'),
                    "timestamp": data.get('last_update')
                })
        
        return {
            "total_events": len(events),
            "events": events
        }
    except Exception as e:
        logger.error(f"Erro ao obter eventos recentes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 