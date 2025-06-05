from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasicCredentials, HTTPBearer
from src.db.connection import get_db_connection
from src.db.models import get_boarding_pass_data
from src.api.auth import get_auth_provider, AuthProvider, basic_security, bearer_security
import os

router = APIRouter()

def get_security_dependency():
    auth_type = os.getenv("AUTH_TYPE", "basic").lower()
    if auth_type == "basic":
        return basic_security
    elif auth_type in ["cognito", "iam", "lambda"]:
        return bearer_security
    return None

# Dynamically get auth provider
def get_current_auth_provider():
    return get_auth_provider()

async def get_current_user(
    credentials: HTTPBasicCredentials = Depends(get_security_dependency() or (lambda: None)),
    token: str = Depends(get_security_dependency() or (lambda: None))
):
    auth_provider = get_current_auth_provider()
    return await auth_provider.authenticate(credentials=credentials, token=token)

@router.get("/api/v1/boarding-pass/{booking_id}")
async def get_boarding_pass(booking_id: str, user: str = Depends(get_current_user)):
    """Retrieve boarding pass details for a given booking ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        result = get_boarding_pass_data(cursor, booking_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Booking not found")
        boarding_pass = {
            "booking_id": result[0],
            "passenger_name": result[1],
            "flight_number": result[2],
            "departure": result[3],
            "destination": result[4],
            "gate": result[5],
            "seat": result[6],
            "boarding_time": result[7].isoformat() if result[7] else None
        }
        return {"status": "success", "boarding_pass": boarding_pass, "user": user}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()