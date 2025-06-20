from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
import os
from config import *
from src.utils.secretload import get_secret

get_secret(api_key_secret_name)

# Define API key security scheme
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)


#API_KEY = os.getenv(api_key_secret_name)

async def get_api_key(api_key: str = Depends(api_key_header)):
    if not api_key or api_key != os.getenv("api_key","api_key"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key