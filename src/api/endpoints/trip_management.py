from fastapi import APIRouter, HTTPException, Query
from src.db.connection import get_db_connection
from src.db.models import (
    get_trip_prices_data, book_trip_data, get_trip_details_data, get_trip_offers_data,
    get_trip_plan_data, search_trips_data, cancel_trip_data, change_trip_data,
    purchase_trip_insurance_data
)

router = APIRouter()

@router.get("/api/v1/trip-prices/{trip_id}")
async def check_trip_prices(trip_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        result = get_trip_prices_data(cursor, trip_id)
        if not result:
            raise HTTPException(status_code=404, detail="Trip not found")
        return {"status": "success", "trip_prices": {"total_price": result[0]}}
    finally:
        cursor.close()
        conn.close()

@router.post("/api/v1/book-trip/")
async def book_trip(passenger_id: str = Query(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        trip_id = book_trip_data(cursor, passenger_id)
        conn.commit()
        return {"status": "success", "trip_id": trip_id}
    finally:
        cursor.close()
        conn.close()

@router.get("/api/v1/trip-details/{trip_id}")
async def check_trip_details(trip_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        result = get_trip_details_data(cursor, trip_id)
        if not result:
            raise HTTPException(status_code=404, detail="Trip not found")
        return {"status": "success", "trip_details": {
            "total_price": result["total_price"], "status": result["status"], "components": result["components"]
        }}
    finally:
        cursor.close()
        conn.close()

@router.get("/api/v1/trip-offers/")
async def check_trip_offers():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        offers = get_trip_offers_data(cursor)
        return {"status": "success", "offers": offers}
    finally:
        cursor.close()
        conn.close()

@router.get("/api/v1/trip-plan/{trip_id}")
async def check_trip_plan(trip_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        plan = get_trip_plan_data(cursor, trip_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Trip plan not found")
        return {"status": "success", "trip_plan": plan}
    finally:
        cursor.close()
        conn.close()

@router.get("/api/v1/search-trip/{departure}/{destination}/{date}")
async def search_trip(departure: str, destination: str, date: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        trips = search_trips_data(cursor, departure, destination, date)
        return {"status": "success", "trips": trips}
    finally:
        cursor.close()
        conn.close()

@router.post("/api/v1/cancel-trip/{trip_id}")
async def cancel_trip(trip_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        updated = cancel_trip_data(cursor, trip_id)
        if not updated:
            raise HTTPException(status_code=404, detail="Trip not found")
        conn.commit()
        return {"status": "success", "trip_status": "Cancelled", "policy": "Free within 48 hours, $100 fee after"}
    finally:
        cursor.close()
        conn.close()

@router.post("/api/v1/change-trip/{trip_id}")
async def change_trip(trip_id: str, new_flight_number: str = Query(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        result = change_trip_data(cursor, trip_id, new_flight_number)
        if not result:
            raise HTTPException(status_code=404, detail="Trip component not found")
        conn.commit()
        return {"status": "success", "trip_component": {
            "component_type": result[0], "flight_number": result[1], "price": result[2]
        }, "policy": "Free within 48 hours, $100 fee after"}
    finally:
        cursor.close()
        conn.close()

@router.post("/api/v1/purchase-trip-insurance/{trip_id}")
async def purchase_trip_insurance(trip_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        insurance_id = purchase_trip_insurance_data(cursor, trip_id)
        conn.commit()
        return {"status": "success", "insurance_id": insurance_id, "terms": "Covers cancellation up to $2,000"}
    finally:
        cursor.close()
        conn.close()