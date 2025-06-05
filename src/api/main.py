from fastapi import FastAPI
from src.api.endpoints import router
import os
from fastapi.openapi.utils import get_openapi

app = FastAPI()

# Include the router
app.include_router(router)

# Customize OpenAPI schema based on AUTH_TYPE
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    auth_type = os.getenv("AUTH_TYPE", "basic").lower()
    openapi_schema = get_openapi(
        title="Airline Customer Conversational Intelligence Platform API",
        version="0.1.0",
        description="API for retrieving airline boarding pass details.",
        routes=app.routes,
    )

    # Remove security schemes when AUTH_TYPE=none
    if auth_type == "none":
        openapi_schema["components"]["securitySchemes"] = {}
        openapi_schema["security"] = []
        for path in openapi_schema["paths"].values():
            for method in path.values():
                if "security" in method:
                    del method["security"]
    else:
        # Define security schemes for other auth types
        if auth_type == "basic":
            openapi_schema["components"]["securitySchemes"] = {
                "basicAuth": {
                    "type": "http",
                    "scheme": "basic",
                }
            }
            openapi_schema["security"] = [{"basicAuth": []}]
        else:  # cognito, iam, lambda
            openapi_schema["components"]["securitySchemes"] = {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
            openapi_schema["security"] = [{"bearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)