from fastapi import FastAPI, Depends
from src.api.endpoints.boarding import router as boarding_router
from src.api.endpoints.flight_management import router as flight_router
from src.api.endpoints.trip_management import router as trip_router
from fastapi.openapi.utils import get_openapi
from src.api.auth import get_api_key

# Set NONPROD based on a command-line argument or default
import sys
nonprod_value = sys.argv[1] if len(sys.argv) > 1 else "True"
os.environ["NONPROD"] = nonprod_value

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "ok"}  # Can be enhanced to check router status if needed

app.include_router(boarding_router, dependencies=[Depends(get_api_key)])
app.include_router(flight_router, dependencies=[Depends(get_api_key)])
app.include_router(trip_router, dependencies=[Depends(get_api_key)])

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Hopjet Airlines Customer Conversational Intelligence Platform (HACCIP)",
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