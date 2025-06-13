
from fastapi import APIRouter, HTTPException, Query
from src.db.connection import get_db_connection
from src.db.models import (
    get_boarding_pass_data, check_in_booking, book_flight_data, get_flight_offers_data,
    get_flight_prices_data, get_flight_reservation_data, get_flight_status_data, search_flights_data,
    get_trip_prices_data, choose_seat_data, get_arrival_time_data, get_departure_time_data,
    book_trip_data, get_trip_details_data, get_trip_offers_data, get_trip_plan_data, search_trips_data,
    cancel_flight_data, change_flight_data, purchase_flight_insurance_data, get_refund_data,
    change_seat_data, cancel_trip_data, change_trip_data, purchase_trip_insurance_data
)

router = APIRouter()

@router.get("/api/v1/boarding-pass/{booking_id}")
async def get_boarding_pass(booking_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        result = get_boarding_pass_data(cursor, booking_id)
        if not result:
            raise HTTPException(status_code=404, detail="Boarding pass not found")
        return {"status": "success", "boarding_pass": {"gate": result[0], "seat": result[1], "boarding_time": result[2], "pdf_url": result[3]}}
    finally:
        cursor.close()
        conn.close()

@router.get("/api/v1/print-boarding-pass/{booking_id}")
async def print_boarding_pass(booking_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        result = get_boarding_pass_data(cursor, booking_id)
        if not result:
            raise HTTPException(status_code=404, detail="Boarding pass not found")
        return {"status": "success", "boarding_pass": {"gate": result[0], "seat": result[1], "boarding_time": result[2], "pdf_url": result[3]}}
    finally:
        cursor.close()
        conn.close()

@router.post("/api/v1/check-in/{booking_id}")
async def check_in(booking_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        result = check_in_booking(cursor, booking_id)
        if not result["updated"]:
            raise HTTPException(status_code=404, detail="Booking not found")
        conn.commit()
        return {
            "status": "success",
            "message": "Check-in successful",
            "boarding_pass": {"gate": result["gate"], "seat": result["seat"], "boarding_time": result["boarding_time"]}
        }
    finally:
        cursor.close()
        conn.close()

@router.post("/api/v1/book-flight/")
async def book_flight(flight_number: str = Query(...), passenger_id: str = Query(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        booking_id = book_flight_data(cursor, flight_number, passenger_id)
        if not booking_id:
            raise HTTPException(status_code=400, detail="Flight not available")
        conn.commit()
        return {"status": "success", "booking_id": booking_id}
    finally:
        cursor.close()
        conn.close()

@router.get("/api/v1/flight-offers/")
async def check_flight_offers():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        offers = get_flight_offers_data(cursor)
        return {"status": "success", "offers": offers}
    finally:
        cursor.close()
        conn.close()

@router.get("/api/v1/flight-prices/{flight_number}")
async def check_flight_prices(flight_number: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        result = get_flight_prices_data(cursor, flight_number)
        if not result:
            raise HTTPException(status_code=404, detail="Flight not found")
        return {"status": "success", "prices": {"price": result[0], "availability": result[1]}}
    finally:
        cursor.close()
        conn.close()

@router.get("/api/v1/flight-reservation/{booking_id}")
async def check_flight_reservation(booking_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        result = get_flight_reservation_data(cursor, booking_id)
        if not result:
            raise HTTPException(status_code=404, detail="Reservation not found")
        return {"status": "success", "reservation": {
            "passenger_id": result[0], "flight_number": result[1], "booking_date": result[2], "status": result[3],
            "total_price": result[4], "departure": result[5], "destination": result[6]
        }}
    finally:
        cursor.close()
        conn.close()

@router.get("/api/v1/flight-status/{flight_number}")
async def check_flight_status(flight_number: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        result = get_flight_status_data(cursor, flight_number)
        if not result:
            raise HTTPException(status_code=404, detail="Flight not found")
        return {"status": "success", "flight_status": {
            "departure": result[0], "destination": result[1], "status": result[2], "departure_time": result[3],
            "arrival_time": result[4], "gate": result[5]
        }}
    finally:
        cursor.close()
        conn.close()

@router.get("/api/v1/search-flight/{departure}/{destination}/{date}")
async def search_flight(departure: str, destination: str, date: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        flights = search_flights_data(cursor, departure, destination, date)
        return {"status": "success", "flights": flights}
    finally:
        cursor.close()
        conn.close()

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

@router.post("/api/v1/choose-seat/{booking_id}")
async def choose_seat(booking_id: str, seat_number: str = Query(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        result = choose_seat_data(cursor, booking_id, seat_number)
        conn.commit()
        return {"status": "success", "seat": {
            "booking_id": booking_id, "flight_number": result["flight_number"],
            "seat_number": seat_number, "additional_fee": result["additional_fee"]
        }}
    finally:
        cursor.close()
        conn.close()

@router.get("/api/v1/arrival-time/{flight_number}")
async def check_arrival_time(flight_number: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        result = get_arrival_time_data(cursor, flight_number)
        if not result:
            raise HTTPException(status_code=404, detail="Flight not found")
        return {"status": "success", "arrival_time": result[0]}
    finally:
        cursor.close()
        conn.close()

@router.get("/api/v1/departure-time/{flight_number}")
async def check_departure_time(flight_number: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        result = get_departure_time_data(cursor, flight_number)
        if not result:
            raise HTTPException(status_code=404, detail="Flight not found")
        return {"status": "success", "departure_time": result[0]}
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

@router.post("/api/v1/cancel-flight/{booking_id}")
async def cancel_flight(booking_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        updated = cancel_flight_data(cursor, booking_id)
        if not updated:
            raise HTTPException(status_code=404, detail="Booking not found")
        conn.commit()
        return {"status": "success", "booking_status": "Cancelled", "policy": "Free within 24 hours, $50 fee after"}
    finally:
        cursor.close()
        conn.close()

@router.post("/api/v1/change-flight/{booking_id}")
async def change_flight(booking_id: str, new_flight_number: str = Query(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        result = change_flight_data(cursor, booking_id, new_flight_number)
        if not result:
            raise HTTPException(status_code=404, detail="Booking not found")
        conn.commit()
        return {"status": "success", "booking": {
            "passenger_id": result[0], "flight_number": result[1], "booking_date": result[2],
            "status": result[3], "total_price": result[4]
        }, "policy": "Free within 24 hours, $75 fee after"}
    finally:
        cursor.close()
        conn.close()

@router.post("/api/v1/purchase-flight-insurance/{booking_id}")
async def purchase_flight_insurance(booking_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        insurance_id = purchase_flight_insurance_data(cursor, booking_id)
        conn.commit()
        return {"status": "success", "insurance_id": insurance_id, "terms": "Covers cancellation up to $1,000"}
    finally:
        cursor.close()
        conn.close()

@router.post("/api/v1/get-refund/{booking_id}")
async def get_refund(booking_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        updated = get_refund_data(cursor, booking_id)
        if not updated:
            raise HTTPException(status_code=404, detail="Booking not found")
        conn.commit()
        return {"status": "success", "booking_status": "Refunded", "policy": "Processed in 5-7 days, 50% penalty for non-refundable"}
    finally:
        cursor.close()
        conn.close()

@router.post("/api/v1/change-seat/{booking_id}")
async def change_seat(booking_id: str, seat_number: str = Query(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        result = change_seat_data(cursor, booking_id, seat_number)
        if not result:
            raise HTTPException(status_code=404, detail="Seat not found")
        conn.commit()
        return {"status": "success", "seat": {
            "flight_number": result[0], "seat_number": result[1], "additional_fee": result[2]
        }, "policy": "$20 fee for changes"}
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