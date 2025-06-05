from fastapi import APIRouter, HTTPException
from src.db.connection import get_db_connection
from src.db.models import get_boarding_pass_data, get_flight_data, get_passenger_data

router = APIRouter()

@router.get("/api/v1/boarding-pass/{booking_id}")
async def get_boarding_pass(booking_id: str):
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
        return {"status": "success", "boarding_pass": boarding_pass}
    finally:
        cursor.close()
        conn.close()

@router.get("/api/v1/flights")
async def get_flights():
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
        return {"status": "success", "flights": flights}
    finally:
        cursor.close()
        conn.close()

@router.get("/api/v1/passengers")
async def get_passengers():
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
        return {"status": "success", "passengers": passengers}
    finally:
        cursor.close()
        conn.close()