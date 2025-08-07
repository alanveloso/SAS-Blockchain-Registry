from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, validator, Field, ValidationError
from typing import Dict, List, Optional, Any, Union
import uvicorn
import logging
import json
import re
from blockchain.blockchain import Blockchain
from repository.repository import CBSDRepository
import asyncio
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

# Middleware para tratamento de erros de validação
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Tratamento personalizado para erros de validação"""
    errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        error_msg = f"{field_path}: {error['msg']}"
        errors.append(error_msg)
    
    logger.warning(f"Erro de validação: {errors}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Erro de validação dos dados",
            "errors": errors,
            "message": "Verifique os campos obrigatórios e formatos",
            "status": "validation_error"
        }
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Tratamento personalizado para erros de validação Pydantic"""
    errors = []
    for error in exc.errors():
        field_path = " -> ".join(str(loc) for loc in error["loc"])
        error_msg = f"{field_path}: {error['msg']}"
        errors.append(error_msg)
    
    logger.warning(f"Erro de validação Pydantic: {errors}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Erro de validação dos dados",
            "errors": errors,
            "message": "Verifique os campos obrigatórios e formatos",
            "status": "validation_error"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Tratamento personalizado para exceções gerais"""
    logger.error(f"Erro não tratado: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "message": "Ocorreu um erro inesperado. Tente novamente.",
            "status": "internal_error"
        }
    )

# Modelos Pydantic para SAS-SAS com validação robusta
class RegistrationRequest(BaseModel):
    fccId: str = Field(..., description="FCC ID do CBSD", min_length=1, max_length=50)
    userId: str = Field(..., description="ID do usuário", min_length=1, max_length=50)
    cbsdSerialNumber: str = Field(..., description="Número de série do CBSD", min_length=1, max_length=50)
    callSign: str = Field(..., description="Indicativo de chamada", min_length=1, max_length=20)
    cbsdCategory: str = Field(..., description="Categoria do CBSD", pattern="^(A|B)$")
    airInterface: str = Field(..., description="Interface aérea", pattern="^(E_UTRA|E_UTRA_CA)$")
    measCapability: List[str] = Field(..., description="Capacidades de medição", min_items=1)
    eirpCapability: int = Field(..., description="Capacidade EIRP em dBm/MHz", ge=0, le=47)
    latitude: int = Field(..., description="Latitude em micrograus", ge=-900000000, le=900000000)
    longitude: int = Field(..., description="Longitude em micrograus", ge=-1800000000, le=1800000000)
    height: int = Field(..., description="Altura em metros", ge=0, le=2000)
    heightType: str = Field(..., description="Tipo de altura", pattern="^(AGL|AMSL)$")
    indoorDeployment: bool = Field(..., description="Implantação interna")
    antennaGain: int = Field(..., description="Ganho da antena em dBi", ge=0, le=30)
    antennaBeamwidth: int = Field(..., description="Largura do feixe em graus", ge=1, le=360)
    antennaAzimuth: int = Field(..., description="Azimute da antena em graus", ge=0, le=359)
    groupingParam: Union[str, List[Dict[str, str]]] = Field(default="", description="Parâmetros de agrupamento")
    cbsdAddress: str = Field(..., description="Endereço do CBSD", min_length=42, max_length=42)

    @validator('fccId')
    def validate_fcc_id(cls, v):
        if not re.match(r'^[A-Z0-9\-_]+$', v):
            raise ValueError('FCC ID deve conter apenas letras maiúsculas, números, hífens e underscores')
        return v

    @validator('cbsdSerialNumber')
    def validate_cbsd_serial(cls, v):
        if not re.match(r'^[A-Z0-9\-_]+$', v):
            raise ValueError('Número de série CBSD deve conter apenas letras maiúsculas, números, hífens e underscores')
        return v

    @validator('callSign')
    def validate_call_sign(cls, v):
        if not re.match(r'^[A-Z0-9]+$', v):
            raise ValueError('Indicativo de chamada deve conter apenas letras maiúsculas e números')
        return v

    @validator('measCapability')
    def validate_meas_capability(cls, v):
        valid_capabilities = [
            'EUTRA_CARRIER_RSSI_NON_TX',
            'EUTRA_CARRIER_RSSI_TX',
            'EUTRA_CARRIER_RSSI',
            'EUTRA_CARRIER_TX_POWER',
            'EUTRA_CARRIER_TX_POWER_NON_TX',
            'EUTRA_CARRIER_TX_POWER_TX'
        ]
        for capability in v:
            if capability not in valid_capabilities:
                raise ValueError(f'Capacidade de medição inválida: {capability}')
        return v

    @validator('groupingParam')
    def validate_grouping_param(cls, v):
        if isinstance(v, list):
            # Validar estrutura do array
            for item in v:
                if not isinstance(item, dict):
                    raise ValueError('Cada item em groupingParam deve ser um objeto')
                if 'groupId' not in item or 'groupType' not in item:
                    raise ValueError('Cada item em groupingParam deve ter groupId e groupType')
            return json.dumps(v)
        elif isinstance(v, str):
            return v
        else:
            raise ValueError('groupingParam deve ser string ou array de objetos')

    @validator('cbsdAddress')
    def validate_cbsd_address(cls, v):
        if not v.startswith('0x'):
            raise ValueError('Endereço CBSD deve começar com 0x')
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError('Endereço CBSD deve ser um endereço Ethereum válido')
        return v.lower()

class GrantRequest(BaseModel):
    fccId: str = Field(..., description="FCC ID do CBSD", min_length=1, max_length=50)
    cbsdSerialNumber: str = Field(..., description="Número de série do CBSD", min_length=1, max_length=50)
    channelType: str = Field(..., description="Tipo de canal", pattern="^(GAA|PAL)$")
    maxEirp: int = Field(..., description="EIRP máximo em dBm/MHz", ge=0, le=47)
    lowFrequency: int = Field(..., description="Frequência baixa em Hz", ge=3550000000, le=3700000000)
    highFrequency: int = Field(..., description="Frequência alta em Hz", ge=3550000000, le=3700000000)
    requestedMaxEirp: int = Field(..., description="EIRP máximo solicitado em dBm/MHz", ge=0, le=47)
    requestedLowFrequency: int = Field(..., description="Frequência baixa solicitada em Hz", ge=3550000000, le=3700000000)
    requestedHighFrequency: int = Field(..., description="Frequência alta solicitada em Hz", ge=3550000000, le=3700000000)
    grantExpireTime: int = Field(..., description="Tempo de expiração do grant", ge=0)

    @validator('fccId')
    def validate_fcc_id(cls, v):
        if not re.match(r'^[A-Z0-9\-_]+$', v):
            raise ValueError('FCC ID deve conter apenas letras maiúsculas, números, hífens e underscores')
        return v

    @validator('cbsdSerialNumber')
    def validate_cbsd_serial(cls, v):
        if not re.match(r'^[A-Z0-9\-_]+$', v):
            raise ValueError('Número de série CBSD deve conter apenas letras maiúsculas, números, hífens e underscores')
        return v

    @validator('highFrequency')
    def validate_frequency_range(cls, v, values):
        if 'lowFrequency' in values and v <= values['lowFrequency']:
            raise ValueError('highFrequency deve ser maior que lowFrequency')
        return v

    @validator('requestedHighFrequency')
    def validate_requested_frequency_range(cls, v, values):
        if 'requestedLowFrequency' in values and v <= values['requestedLowFrequency']:
            raise ValueError('requestedHighFrequency deve ser maior que requestedLowFrequency')
        return v

class HeartbeatRequest(BaseModel):
    fccId: str = Field(..., description="FCC ID do CBSD", min_length=1, max_length=50)
    cbsdSerialNumber: str = Field(..., description="Número de série do CBSD", min_length=1, max_length=50)
    grantId: str = Field(..., description="ID do grant", min_length=1, max_length=50)
    transmitExpireTime: Optional[int] = Field(None, description="Tempo de expiração da transmissão", ge=0)

    @validator('fccId')
    def validate_fcc_id(cls, v):
        if not re.match(r'^[A-Z0-9\-_]+$', v):
            raise ValueError('FCC ID deve conter apenas letras maiúsculas, números, hífens e underscores')
        return v

    @validator('cbsdSerialNumber')
    def validate_cbsd_serial(cls, v):
        if not re.match(r'^[A-Z0-9\-_]+$', v):
            raise ValueError('Número de série CBSD deve conter apenas letras maiúsculas, números, hífens e underscores')
        return v

class RelinquishmentRequest(BaseModel):
    fccId: str = Field(..., description="FCC ID do CBSD", min_length=1, max_length=50)
    cbsdSerialNumber: str = Field(..., description="Número de série do CBSD", min_length=1, max_length=50)
    grantId: str = Field(..., description="ID do grant", min_length=1, max_length=50)

    @validator('fccId')
    def validate_fcc_id(cls, v):
        if not re.match(r'^[A-Z0-9\-_]+$', v):
            raise ValueError('FCC ID deve conter apenas letras maiúsculas, números, hífens e underscores')
        return v

    @validator('cbsdSerialNumber')
    def validate_cbsd_serial(cls, v):
        if not re.match(r'^[A-Z0-9\-_]+$', v):
            raise ValueError('Número de série CBSD deve conter apenas letras maiúsculas, números, hífens e underscores')
        return v

class DeregistrationRequest(BaseModel):
    fccId: str = Field(..., description="FCC ID do CBSD", min_length=1, max_length=50)
    cbsdSerialNumber: str = Field(..., description="Número de série do CBSD", min_length=1, max_length=50)

    @validator('fccId')
    def validate_fcc_id(cls, v):
        if not re.match(r'^[A-Z0-9\-_]+$', v):
            raise ValueError('FCC ID deve conter apenas letras maiúsculas, números, hífens e underscores')
        return v

    @validator('cbsdSerialNumber')
    def validate_cbsd_serial(cls, v):
        if not re.match(r'^[A-Z0-9\-_]+$', v):
            raise ValueError('Número de série CBSD deve conter apenas letras maiúsculas, números, hífens e underscores')
        return v

class SASAuthorization(BaseModel):
    sas_address: str = Field(..., description="Endereço SAS", min_length=42, max_length=42)

    @validator('sas_address')
    def validate_sas_address(cls, v):
        if not v.startswith('0x'):
            raise ValueError('Endereço SAS deve começar com 0x')
        if not re.match(r'^0x[a-fA-F0-9]{40}$', v):
            raise ValueError('Endereço SAS deve ser um endereço Ethereum válido')
        return v.lower()

# Modelos com chave privada
class RegistrationRequestWithKey(RegistrationRequest):
    private_key: str = Field(..., description="Chave privada para assinatura", min_length=66, max_length=66)

    @validator('private_key')
    def validate_private_key(cls, v):
        if not v.startswith('0x'):
            raise ValueError('Chave privada deve começar com 0x')
        if not re.match(r'^0x[a-fA-F0-9]{64}$', v):
            raise ValueError('Chave privada deve ter 64 caracteres hexadecimais')
        return v

class GrantRequestWithKey(GrantRequest):
    private_key: str = Field(..., description="Chave privada para assinatura", min_length=66, max_length=66)

    @validator('private_key')
    def validate_private_key(cls, v):
        if not v.startswith('0x'):
            raise ValueError('Chave privada deve começar com 0x')
        if not re.match(r'^0x[a-fA-F0-9]{64}$', v):
            raise ValueError('Chave privada deve ter 64 caracteres hexadecimais')
        return v

class RelinquishmentRequestWithKey(RelinquishmentRequest):
    private_key: str = Field(..., description="Chave privada para assinatura", min_length=66, max_length=66)

    @validator('private_key')
    def validate_private_key(cls, v):
        if not v.startswith('0x'):
            raise ValueError('Chave privada deve começar com 0x')
        if not re.match(r'^0x[a-fA-F0-9]{64}$', v):
            raise ValueError('Chave privada deve ter 64 caracteres hexadecimais')
        return v

class DeregistrationRequestWithKey(DeregistrationRequest):
    private_key: str = Field(..., description="Chave privada para assinatura", min_length=66, max_length=66)

    @validator('private_key')
    def validate_private_key(cls, v):
        if not v.startswith('0x'):
            raise ValueError('Chave privada deve começar com 0x')
        if not re.match(r'^0x[a-fA-F0-9]{64}$', v):
            raise ValueError('Chave privada deve ter 64 caracteres hexadecimais')
        return v

class SASAuthorizationWithKey(SASAuthorization):
    private_key: str = Field(..., description="Chave privada para assinatura", min_length=66, max_length=66)

    @validator('private_key')
    def validate_private_key(cls, v):
        if not v.startswith('0x'):
            raise ValueError('Chave privada deve começar com 0x')
        if not re.match(r'^0x[a-fA-F0-9]{64}$', v):
            raise ValueError('Chave privada deve ter 64 caracteres hexadecimais')
        return v

# Funções auxiliares para validação e sanitização
def sanitize_ethereum_address(address: str) -> str:
    """Sanitiza endereço Ethereum"""
    if not address:
        raise ValueError("Endereço não pode ser vazio")
    
    # Remove espaços e converte para minúsculas
    address = address.strip().lower()
    
    # Valida formato
    if not re.match(r'^0x[a-f0-9]{40}$', address):
        raise ValueError("Endereço Ethereum inválido")
    
    return address

def sanitize_private_key(private_key: str) -> str:
    """Sanitiza chave privada"""
    if not private_key:
        raise ValueError("Chave privada não pode ser vazia")
    
    # Remove espaços e converte para minúsculas
    private_key = private_key.strip().lower()
    
    # Valida formato
    if not re.match(r'^0x[a-f0-9]{64}$', private_key):
        raise ValueError("Chave privada inválida")
    
    return private_key

def validate_frequency_range(low: int, high: int) -> bool:
    """Valida range de frequência"""
    if low < 3550000000 or high > 3700000000:
        raise ValueError("Frequência fora do range permitido (3.55-3.7 GHz)")
    if high <= low:
        raise ValueError("Frequência alta deve ser maior que frequência baixa")
    return True

def validate_eirp_range(eirp: int) -> bool:
    """Valida range de EIRP"""
    if eirp < 0 or eirp > 47:
        raise ValueError("EIRP deve estar entre 0 e 47 dBm/MHz")
    return True

def validate_coordinates(lat: int, lon: int) -> bool:
    """Valida coordenadas geográficas"""
    if lat < -900000000 or lat > 900000000:
        raise ValueError("Latitude deve estar entre -90 e 90 graus")
    if lon < -1800000000 or lon > 1800000000:
        raise ValueError("Longitude deve estar entre -180 e 180 graus")
    return True

def validate_antenna_params(gain: int, beamwidth: int, azimuth: int) -> bool:
    """Valida parâmetros da antena"""
    if gain < 0 or gain > 30:
        raise ValueError("Ganho da antena deve estar entre 0 e 30 dBi")
    if beamwidth < 1 or beamwidth > 360:
        raise ValueError("Largura do feixe deve estar entre 1 e 360 graus")
    if azimuth < 0 or azimuth > 359:
        raise ValueError("Azimute deve estar entre 0 e 359 graus")
    return True

def sanitize_string_field(value: str, field_name: str, max_length: int = 50) -> str:
    """Sanitiza campo string"""
    if not value:
        raise ValueError(f"{field_name} não pode ser vazio")
    
    # Remove espaços extras
    value = value.strip()
    
    # Valida comprimento
    if len(value) > max_length:
        raise ValueError(f"{field_name} deve ter no máximo {max_length} caracteres")
    
    return value

def validate_cbsd_category(category: str) -> str:
    """Valida categoria CBSD"""
    valid_categories = ['A', 'B']
    if category not in valid_categories:
        raise ValueError(f"Categoria CBSD deve ser uma das seguintes: {valid_categories}")
    return category

def validate_air_interface(interface: str) -> str:
    """Valida interface aérea"""
    valid_interfaces = ['E_UTRA', 'E_UTRA_CA']
    if interface not in valid_interfaces:
        raise ValueError(f"Interface aérea deve ser uma das seguintes: {valid_interfaces}")
    return interface

def validate_channel_type(channel_type: str) -> str:
    """Valida tipo de canal"""
    valid_types = ['GAA', 'PAL']
    if channel_type not in valid_types:
        raise ValueError(f"Tipo de canal deve ser um dos seguintes: {valid_types}")
    return channel_type

def validate_height_type(height_type: str) -> str:
    """Valida tipo de altura"""
    valid_types = ['AGL', 'AMSL']
    if height_type not in valid_types:
        raise ValueError(f"Tipo de altura deve ser um dos seguintes: {valid_types}")
    return height_type

def validate_meas_capability(capabilities: List[str]) -> List[str]:
    """Valida capacidades de medição"""
    valid_capabilities = [
        'EUTRA_CARRIER_RSSI_NON_TX',
        'EUTRA_CARRIER_RSSI_TX',
        'EUTRA_CARRIER_RSSI',
        'EUTRA_CARRIER_TX_POWER',
        'EUTRA_CARRIER_TX_POWER_NON_TX',
        'EUTRA_CARRIER_TX_POWER_TX'
    ]
    
    for capability in capabilities:
        if capability not in valid_capabilities:
            raise ValueError(f"Capacidade de medição inválida: {capability}")
    
    return capabilities

def process_grouping_param(grouping_param: Union[str, List[Dict[str, str]]]) -> str:
    """Processa parâmetros de agrupamento"""
    if isinstance(grouping_param, list):
        # Validar estrutura do array
        for item in grouping_param:
            if not isinstance(item, dict):
                raise ValueError("Cada item em groupingParam deve ser um objeto")
            if 'groupId' not in item or 'groupType' not in item:
                raise ValueError("Cada item em groupingParam deve ter groupId e groupType")
        return json.dumps(grouping_param)
    elif isinstance(grouping_param, str):
        return grouping_param
    else:
        raise ValueError("groupingParam deve ser string ou array de objetos")

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
        # Print para debug
        logger.info(f"=== REGISTRATION DEBUG ===")
        logger.info(f"fccId: {req.fccId}")
        logger.info(f"userId: {req.userId}")
        logger.info(f"cbsdSerialNumber: {req.cbsdSerialNumber}")
        logger.info(f"cbsdAddress: {req.cbsdAddress}")
        logger.info(f"private_key: {req.private_key[:10]}...")
        logger.info(f"==========================")
        
        blockchain = Blockchain(req.private_key)
        receipt = await blockchain.registration_with_nonce_manager(req.dict(exclude={"private_key"}))
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
        # Print para debug
        logger.info(f"=== GRANT DEBUG ===")
        logger.info(f"fccId: {req.fccId}")
        logger.info(f"cbsdSerialNumber: {req.cbsdSerialNumber}")
        logger.info(f"private_key: {req.private_key[:10]}...")
        logger.info(f"===================")
        
        blockchain = Blockchain(req.private_key)
        receipt = await blockchain.grant_with_nonce_manager(req.dict(exclude={"private_key"}))
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
        # Print para debug
        logger.info(f"=== RELINQUISHMENT DEBUG ===")
        logger.info(f"fccId: {req.fccId}")
        logger.info(f"cbsdSerialNumber: {req.cbsdSerialNumber}")
        logger.info(f"grantId: {req.grantId}")
        logger.info(f"private_key: {req.private_key[:10]}...")
        logger.info(f"============================")
        
        blockchain = Blockchain(req.private_key)
        receipt = await blockchain.relinquishment_with_nonce_manager(req.dict(exclude={"private_key"}))
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
        # Print para debug
        logger.info(f"=== DEREGISTRATION DEBUG ===")
        logger.info(f"fccId: {req.fccId}")
        logger.info(f"cbsdSerialNumber: {req.cbsdSerialNumber}")
        logger.info(f"private_key: {req.private_key[:10]}...")
        logger.info(f"============================")
        
        blockchain = Blockchain(req.private_key)
        receipt = await blockchain.deregistration_with_nonce_manager(req.dict(exclude={"private_key"}))
        return {
            "success": True,
            "message": f"Deregistration executado para {req.fccId}/{req.cbsdSerialNumber} via SAS-SAS",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro no deregistration SAS-SAS: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Endpoints assíncronos

@app.post("/v1.3/registration/async")
async def registration_async(req: RegistrationRequestWithKey):
    """Endpoint assíncrono para registration (não aguarda confirmação)"""
    try:
        blockchain = Blockchain(req.private_key)
        result = await blockchain.registration_async(req.dict())
        return {
            "success": True,
            "message": "Registration submetido assincronamente",
            "transaction_hash": result['transaction_hash'],
            "status": result['status'],
            "nonce": result['nonce']
        }
    except Exception as e:
        logger.error(f"Erro no registration assíncrono: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1.3/grant/async")
async def grant_spectrum_async(req: GrantRequestWithKey):
    """Endpoint assíncrono para grant (não aguarda confirmação)"""
    try:
        blockchain = Blockchain(req.private_key)
        result = await blockchain.grant_async(req.dict())
        return {
            "success": True,
            "message": "Grant submetido assincronamente",
            "transaction_hash": result['transaction_hash'],
            "status": result['status'],
            "nonce": result['nonce']
        }
    except Exception as e:
        logger.error(f"Erro no grant assíncrono: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1.3/relinquishment/async")
async def relinquishment_async(req: RelinquishmentRequestWithKey):
    """Endpoint assíncrono para relinquishment (não aguarda confirmação)"""
    try:
        blockchain = Blockchain(req.private_key)
        result = await blockchain.relinquishment_async(req.dict())
        return {
            "success": True,
            "message": "Relinquishment submetido assincronamente",
            "transaction_hash": result['transaction_hash'],
            "status": result['status'],
            "nonce": result['nonce']
        }
    except Exception as e:
        logger.error(f"Erro no relinquishment assíncrono: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/v1.3/deregistration/async")
async def deregistration_async(req: DeregistrationRequestWithKey):
    """Endpoint assíncrono para deregistration (não aguarda confirmação)"""
    try:
        blockchain = Blockchain(req.private_key)
        result = await blockchain.deregistration_async(req.dict())
        return {
            "success": True,
            "message": "Deregistration submetido assincronamente",
            "transaction_hash": result['transaction_hash'],
            "status": result['status'],
            "nonce": result['nonce']
        }
    except Exception as e:
        logger.error(f"Erro no deregistration assíncrono: {e}")
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
        receipt = await blockchain.authorize_sas_with_nonce_manager(req.sas_address)
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
        receipt = await blockchain.revoke_sas_with_nonce_manager(req.sas_address)
        return {
            "success": True,
            "message": f"SAS {req.sas_address} revogado",
            "transaction_hash": receipt['transactionHash'].hex(),
            "block_number": receipt['blockNumber']
        }
    except Exception as e:
        logger.error(f"Erro ao revogar SAS: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Endpoints assíncronos de autorização SAS

@app.post("/sas/authorize/async")
async def authorize_sas_async(req: SASAuthorizationWithKey):
    """Endpoint assíncrono para authorize SAS (não aguarda confirmação)"""
    try:
        blockchain = Blockchain(req.private_key)
        result = await blockchain.authorize_sas_async(req.sas_address)
        return {
            "success": True,
            "message": f"SAS {req.sas_address} autorização submetida assincronamente",
            "transaction_hash": result['transaction_hash'],
            "status": result['status'],
            "nonce": result['nonce']
        }
    except Exception as e:
        logger.error(f"Erro ao autorizar SAS assíncrono: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/sas/revoke/async")
async def revoke_sas_async(req: SASAuthorizationWithKey):
    """Endpoint assíncrono para revoke SAS (não aguarda confirmação)"""
    try:
        blockchain = Blockchain(req.private_key)
        result = await blockchain.revoke_sas_async(req.sas_address)
        return {
            "success": True,
            "message": f"SAS {req.sas_address} revogação submetida assincronamente",
            "transaction_hash": result['transaction_hash'],
            "status": result['status'],
            "nonce": result['nonce']
        }
    except Exception as e:
        logger.error(f"Erro ao revogar SAS assíncrono: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Endpoints de informações

@app.get("/nonce-pool/stats")
async def get_nonce_pool_stats():
    """Obtém estatísticas do NoncePool"""
    try:
        nonce_pool_stats = blockchain.get_nonce_manager_stats()
        return {
            "nonce_pool_stats": nonce_pool_stats,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas do NoncePool: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/stats")
async def get_stats():
    """Obtém estatísticas do contrato"""
    try:
        owner = blockchain.get_owner()
        latest_block = blockchain.get_latest_block()
        nonce_pool_stats = blockchain.get_nonce_manager_stats()
        return {
            "owner": owner,
            "contract_address": blockchain.contract.address,
            "latest_block": latest_block,
            "version": "3.0.0 (SAS-SAS)",
            "nonce_pool_stats": nonce_pool_stats
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