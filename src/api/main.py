
from fastapi import FastAPI, Depends, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from src.api.endpoints.boarding import router as boarding_router
from src.api.endpoints.flight_management import router as flight_router
from src.api.endpoints.trip_management import router as trip_router
from fastapi.openapi.utils import get_openapi
from src.api.auth import get_api_key


from src.db.connection import get_db_connection, open_db_pool, close_db_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application's startup and shutdown events.
    Opens the database pool on startup and closes it on shutdown.
    """
    print("Application startup: Initializing database pool...")
    await open_db_pool()
    
    yield  # The application runs after this point
    
    print("Application shutdown: Closing database pool...")
    await close_db_pool()



app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check():
    # Lightweight check for ALB
    return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok"})


@app.get("/health-deep")
async def health_deep():
    # db check for docker & task
    try:
        async with get_db_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                return JSONResponse(status_code=status.HTTP_200_OK, content={"status": "ok", "db": "reachable"})
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "fail", "error": str(e)}
        )

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
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"ApiKeyAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)