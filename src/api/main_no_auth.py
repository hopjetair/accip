from fastapi import FastAPI
from src.api.endpoints_no_auth import router
from fastapi.openapi.utils import get_openapi

app = FastAPI()

# Include the router
app.include_router(router)

# Customize OpenAPI schema (no authentication)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Airline Customer Conversational Intelligence Platform (No Auth)",
        version="0.1.0",
        description="API for retrieving airline data without authentication.",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {}
    openapi_schema["security"] = []
    for path in openapi_schema["paths"].values():
        for method in path.values():
            if "security" in method:
                del method["security"]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
    
