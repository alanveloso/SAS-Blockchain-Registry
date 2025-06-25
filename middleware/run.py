#!/usr/bin/env python3
"""
SAS Blockchain Registry Middleware
Simplified entry point
"""

import uvicorn
import logging
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import the API
from api.api import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🚀 Iniciando SAS Blockchain Registry Middleware...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9000,
        reload=False,
        log_level="info"
    ) 