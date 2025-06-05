from abc import ABC, abstractmethod
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
import os
from jose import jwt, JWTError
import boto3

# Security dependencies
basic_security = HTTPBasic()
bearer_security = HTTPBearer()

class AuthProvider(ABC):
    @abstractmethod
    async def authenticate(self, credentials=None, token=None):
        pass

class BasicAuthProvider(AuthProvider):
    async def authenticate(self, credentials=None, token=None):
        if not credentials:
            raise HTTPException(status_code=401, detail="No credentials provided", headers={"WWW-Authenticate": "Basic"})
        correct_username = "admin"
        correct_password = "password123"
        if credentials.username != correct_username or credentials.password != correct_password:
            raise HTTPException(status_code=403, detail="Incorrect username or password", headers={"WWW-Authenticate": "Basic"})
        return credentials.username

class CognitoAuthProvider(AuthProvider):
    async def authenticate(self, credentials=None, token=None):
        if not token:
            raise HTTPException(status_code=401, detail="No token provided", headers={"WWW-Authenticate": "Bearer"})
        try:
            # Mock token for testing; in production, use a real key
            decoded_token = jwt.decode(token, "mock_key", options={"verify_signature": False})
            username = decoded_token.get("username", "cognito_user")  # Default for mock
            if not username:
                raise HTTPException(status_code=403, detail="Invalid token")
            return username
        except JWTError:
            raise HTTPException(status_code=403, detail="Invalid token")

class IamAuthProvider(AuthProvider):
    async def authenticate(self, credentials=None, token=None):
        if not token:
            raise HTTPException(status_code=401, detail="No IAM credentials provided")
        return "iam_user"  # Placeholder

class LambdaAuthorizerProvider(AuthProvider):
    async def authenticate(self, credentials=None, token=None):
        if not token:
            raise HTTPException(status_code=401, detail="No token provided")
        return "lambda_user"  # Mock response

class NoAuthProvider(AuthProvider):
    async def authenticate(self, credentials=None, token=None):
        return "anonymous"

def get_auth_provider():
    """Return the appropriate AuthProvider based on environment variable."""
    auth_type = os.getenv("AUTH_TYPE", "basic").lower()
    print(f"AUTH_TYPE is set to: {auth_type}")  # Debug statement
    if auth_type == "cognito":
        return CognitoAuthProvider()
    elif auth_type == "iam":
        return IamAuthProvider()
    elif auth_type == "lambda":
        return LambdaAuthorizerProvider()
    elif auth_type == "none":
        return NoAuthProvider()
    else:
        return BasicAuthProvider()