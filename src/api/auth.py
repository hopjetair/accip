from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

# Define API key security scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# List of valid API keys (for testing; in production, use a secure storage like environment variables)
API_KEYS = ["my-secret-key", "another-secret-key"]

async def get_api_key(api_key: str = Depends(api_key_header)):
    if not api_key or api_key not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key