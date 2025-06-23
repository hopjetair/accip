from fastapi import APIRouter, HTTPException
from src.db.connection import get_db_connection
from src.db.models import (
    get_boarding_pass_data, check_in_booking, choose_seat_data, change_seat_data
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
        return {"status": "success", "boarding_pass": {"gate": result[5], "seat": result[6], "boarding_time": result[7], "pdf_url": result[8]}}
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

@router.post("/api/v1/choose-seat/{booking_id}")
async def choose_seat(booking_id: str, seat_number: str):
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

@router.post("/api/v1/change-seat/{booking_id}")
async def change_seat(booking_id: str, seat_number: str):
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