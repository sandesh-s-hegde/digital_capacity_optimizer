import os
import secrets
import logging
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

logger = logging.getLogger("digital-twin")

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    expected_key = os.getenv("OPTIMIZER_API_KEY", "dev_optimizer_key")

    if not api_key:
        logger.warning("Rejected request: Missing X-API-Key header.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key validation."
        )

    if not secrets.compare_digest(api_key, expected_key):
        logger.error("Rejected request: Invalid API Key provided.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid cryptographic credentials."
        )

    return api_key
