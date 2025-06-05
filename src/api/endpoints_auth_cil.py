from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from src.db.connection import get_db_connection
from src.db.models import get_boarding_pass_data, get_flight_data, get_passenger_data
from src.api.auth import get_auth_provider, AuthProvider, bearer_security

router = APIRouter()

auth_provider = get_auth_provider()

async def get_current_user(token: str = Depends(bearer_security)):
    return await auth_provider.authenticate(token=token)

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
    finally:
        cursor.close()
        conn.close()

@router.get("/api/v1/flights")
async def get_flights(user: str = Depends(get_current_user)):
    """Retrieve a list of all flights."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT flight_number, departure, destination, departure_time FROM flights")
        results = cursor.fetchall()
        flights = [
            {
                "flight_number": row[0],
                "departure": row[1],
                "destination": row[2],
                "departure_time": row[3].isoformat() if row[3] else None
            }
            for row in results
        ]
        return {"status": "success", "flights": flights, "user": user}
    finally:
        cursor.close()
        conn.close()

@router.get("/api/v1/passengers")
async def get_passengers(user: str = Depends(get_current_user)):
    """Retrieve a list of all passengers."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT passenger_id, name, email FROM passengers")
        results = cursor.fetchall()
        passengers = [
            {"passenger_id": row[0], "name": row[1], "email": row[2]}
            for row in results
        ]
        return {"status": "success", "passengers": passengers, "user": user}
    finally:
        cursor.close()
        conn.close()