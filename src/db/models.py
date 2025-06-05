import psycopg2
from datetime import datetime

def get_boarding_pass_data(cursor, booking_id):
    """Fetch boarding pass data for a given booking ID."""
    cursor.execute(
        "SELECT b.booking_id, p.name, f.flight_number, f.departure, f.destination, bp.gate, bp.seat, bp.boarding_time "
        "FROM Bookings b "
        "JOIN Passengers p ON b.passenger_id = p.passenger_id "
        "JOIN Flights f ON b.flight_number = f.flight_number "
        "JOIN Boarding_Passes bp ON b.booking_id = bp.booking_id "
        "WHERE b.booking_id = %s",
        (booking_id,)
    )
    return cursor.fetchone()