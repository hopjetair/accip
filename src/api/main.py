from fastapi import FastAPI, Depends
from src.api.endpoints import router
from src.api.auth import get_api_key
from fastapi.openapi.utils import get_openapi

from src.api.auth import get_api_key
import os
from src.utils.secretload import get_secret
from config import api_key_secret_name


get_secret(api_key_secret_name)

app = FastAPI()



# Include the router with the API key dependency
app.include_router(router, dependencies=[Depends(get_api_key)])

# Customize OpenAPI schema (no authentication in schema for simplicity)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Airline Customer Conversational Intelligence Platform (ACCIP)",
        version="0.1.0",
        description="API for retrieving airline data with API key authentication.",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"}
    }
    openapi_schema["security"] = [{"ApiKeyAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)