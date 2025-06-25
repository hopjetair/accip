from src.db.connection import get_db_connection
from psycopg2 import Error


def get_boarding_pass_data(cursor, booking_id):
    try:
        cursor.execute(
            "SELECT b.booking_id, p.name, f.flight_number, f.departure, f.destination, bp.gate, bp.seat, bp.boarding_time, bp.pdf_url "
            "FROM Bookings b "
            "JOIN Passengers p ON b.passenger_id = p.passenger_id "
            "JOIN Flights f ON b.flight_number = f.flight_number "
            "JOIN Boarding_Passes bp ON b.booking_id = bp.booking_id "
            "WHERE b.booking_id = %s",
            (booking_id,)
        )
        result = cursor.fetchone()

        return result
    except Error as e:
        raise Exception(f"Query failed: {e}")

def check_in_booking(cursor, booking_id):
    try:
        cursor.execute("UPDATE Bookings SET status = 'Checked In' WHERE booking_id = %s", (booking_id,))
        updated = cursor.rowcount > 0
        if updated:
            next_boarding_pass_id = get_next_boarding_pass_id(cursor)
            cursor.execute(
                "INSERT INTO Boarding_Passes (boarding_pass_id, booking_id, gate, seat, boarding_time, pdf_url) VALUES (%s, %s, %s, %s, %s, %s)",
                (next_boarding_pass_id, booking_id, "B5", "5B", "2025-06-08T09:30:00", f"https://airline.com/boardingpass/{booking_id}.pdf")
            )
        return {
            "updated": updated,
            "gate": "B5",
            "seat": "5B",
            "boarding_time": "2025-06-08T09:30:00"
        }
    except Error as e:
        raise Exception(f"Query failed: {e}")

def book_flight_data(cursor, flight_number, passenger_id):
    try:
        booking_id = "B" + str(hash(passenger_id + flight_number))[:6]
        cursor.execute("SELECT booking_id FROM bookings WHERE booking_id = %s", (booking_id,))
        result = cursor.fetchone()
        if not result:
            cursor.execute("SELECT price, availability FROM Flights WHERE flight_number = %s", (flight_number,))
            result = cursor.fetchone()
            if not result or result[1] <= 0:
                return None
            cursor.execute(
                "INSERT INTO Bookings (booking_id, passenger_id, flight_number, booking_date, status, total_price) VALUES (%s, %s, %s, %s, %s, %s)",
                (booking_id, passenger_id, flight_number, "2025-06-03", "Confirmed", result[0])
            )
            cursor.execute("UPDATE Flights SET availability = availability - 1 WHERE flight_number = %s", (flight_number,))
        return booking_id
    except Error as e:
        raise Exception(f"Query failed: {e}")

def get_flight_offers_data(cursor):
    try:
        cursor.execute("SELECT description, price, discount FROM Offers WHERE offer_type = 'Flight'")
        return [{"description": row[0], "price": row[1], "discount": row[2]} for row in cursor.fetchall()]
    except Error as e:
        raise Exception(f"Query failed: {e}")

def get_flight_prices_data(cursor, flight_number):
    try:
        cursor.execute("SELECT price, availability FROM Flights WHERE flight_number = %s", (flight_number,))
        return cursor.fetchone()
    except Error as e:
        raise Exception(f"Query failed: {e}")

def get_flight_reservation_data(cursor, booking_id):
    try:
        cursor.execute(
            "SELECT b.passenger_id, b.flight_number, b.booking_date, b.status, b.total_price, f.departure, f.destination "
            "FROM Bookings b JOIN Flights f ON b.flight_number = f.flight_number WHERE b.booking_id = %s",
            (booking_id,)
        )
        return cursor.fetchone()
    except Error as e:
        raise Exception(f"Query failed: {e}")

def get_flight_status_data(cursor, flight_number):
    try:
        cursor.execute(
            "SELECT departure, destination, status, departure_time, arrival_time, gate FROM Flights WHERE flight_number = %s",
            (flight_number,)
        )
        return cursor.fetchone()
    except Error as e:
        raise Exception(f"Query failed: {e}")

def search_flights_data(cursor, departure, destination, date):
    try:
        cursor.execute(
            "SELECT flight_number, departure, destination, departure_time, price, availability FROM Flights "
            "WHERE departure = %s AND destination = %s AND departure_time >= %s",
            (departure, destination, f"{date} 00:00:00")
        )
        return [{"flight_number": row[0], "departure": row[1], "destination": row[2], "departure_time": row[3], "price": row[4], "availability": row[5]} for row in cursor.fetchall()]
    except Error as e:
        raise Exception(f"Query failed: {e}")

def get_trip_prices_data(cursor, trip_id):
    try:
        cursor.execute("SELECT total_price FROM Trips WHERE trip_id = %s", (trip_id,))
        return cursor.fetchone()
    except Error as e:
        raise Exception(f"Query failed: {e}")

def choose_seat_data(cursor, booking_id, seat_number):
    try:
        booked_seat = get_booked_seat(cursor, booking_id,seat_number)
        if not booked_seat:
            booked_seat = get_boarding_pass_data(cursor, booking_id)
            cursor.execute(
                "INSERT INTO Seats (booking_id, flight_number, seat_number, additional_fee) VALUES (%s, %s, %s, %s)",
                (booking_id, booked_seat[2], seat_number, 0.00)
            )
        return {"flight_number": booked_seat[2], "additional_fee": 0.00}
    except Error as e:
        raise Exception(f"Query failed: {e}")

def get_arrival_time_data(cursor, flight_number):
    try:
        cursor.execute("SELECT arrival_time FROM Flights WHERE flight_number = %s", (flight_number,))
        return cursor.fetchone()
    except Error as e:
        raise Exception(f"Query failed: {e}")

def get_departure_time_data(cursor, flight_number):
    try:
        cursor.execute("SELECT departure_time FROM Flights WHERE flight_number = %s", (flight_number,))
        return cursor.fetchone()
    except Error as e:
        raise Exception(f"Query failed: {e}")

def book_trip_data(cursor, passenger_id):
    try:
        trip_id = "T" + str(hash(passenger_id + "2025-06-03"))[:6]
        cursor.execute("SELECT trip_id FROM Trips WHERE trip_id = %s", (trip_id,))
        result = cursor.fetchone()
        if not result:        
            cursor.execute("SELECT flight_number FROM Flights ORDER BY RANDOM() LIMIT 1")
            flight = cursor.fetchone()
            cursor.execute("INSERT INTO Trips (trip_id, passenger_id, total_price) VALUES (%s, %s, %s)", (trip_id, passenger_id, 750.00))
            cursor.execute("INSERT INTO Trip_Components (trip_id, component_type, flight_number, price) VALUES (%s, %s, %s, %s)", (trip_id, "Flight", flight[0], 600.00))
        return trip_id
    except Error as e:
        raise Exception(f"Query failed: {e}")

def get_trip_details_data(cursor, trip_id):
    try:
        cursor.execute("SELECT total_price, status FROM Trips WHERE trip_id = %s", (trip_id,))
        trip = cursor.fetchone()
        if not trip:
            return None
        cursor.execute("SELECT component_type, flight_number, price FROM Trip_Components WHERE trip_id = %s", (trip_id,))
        components = [{"component_type": row[0], "flight_number": row[1], "price": row[2]} for row in cursor.fetchall()]
        return {"total_price": trip[0], "status": trip[1], "components": components}
    except Error as e:
        raise Exception(f"Query failed: {e}")

def get_trip_offers_data(cursor):
    try:
        cursor.execute("SELECT description, price, discount FROM Offers WHERE offer_type = 'Trip'")
        return [{"description": row[0], "price": row[1], "discount": row[2]} for row in cursor.fetchall()]
    except Error as e:
        raise Exception(f"Query failed: {e}")

def get_trip_plan_data(cursor, trip_id):
    try:
        cursor.execute("SELECT component_type, flight_number, price FROM Trip_Components WHERE trip_id = %s", (trip_id,))
        return [{"component_type": row[0], "flight_number": row[1], "price": row[2]} for row in cursor.fetchall()]
    except Error as e:
        raise Exception(f"Query failed: {e}")

def search_trips_data(cursor, departure, destination, date):
    try:
        cursor.execute(
            "SELECT t.trip_id, t.total_price FROM Trips t JOIN Trip_Components tc ON t.trip_id = tc.trip_id "
            "JOIN Flights f ON tc.flight_number = f.flight_number WHERE f.departure = %s AND f.destination = %s AND f.departure_time >= %s",
            (departure, destination, f"{date} 00:00:00")
        )
        return [{"trip_id": row[0], "total_price": row[1]} for row in cursor.fetchall()]
    except Error as e:
        raise Exception(f"Query failed: {e}")

def cancel_flight_data(cursor, booking_id):
    try:
        cursor.execute("UPDATE Bookings SET status = 'Cancelled' WHERE booking_id = %s", (booking_id,))
        return cursor.rowcount > 0
    except Error as e:
        raise Exception(f"Query failed: {e}")

def change_flight_data(cursor, booking_id, new_flight_number):
    try:
        cursor.execute("UPDATE Bookings SET flight_number = %s WHERE booking_id = %s", (new_flight_number, booking_id))
        if cursor.rowcount == 0:
            return None
        cursor.execute(
            "SELECT passenger_id, flight_number, booking_date, status, total_price FROM Bookings WHERE booking_id = %s",
            (booking_id,)
        )
        return cursor.fetchone()
    except Error as e:
        raise Exception(f"Query failed: {e}")

def purchase_flight_insurance_data(cursor, booking_id):
    try:
        insurance_id = "INS" + str(hash(booking_id + "2025-06-03"))[:6]
        cursor.execute("SELECT insurance_id FROM Insurance WHERE insurance_id = %s", (insurance_id,))
        result = cursor.fetchone()
        if not result:
            cursor.execute(
                "INSERT INTO Insurance (insurance_id, booking_id, coverage_type, coverage_amount, premium) "
                "VALUES (%s, %s, %s, %s, %s)",
                (insurance_id, booking_id, "Flight", 1000.00, 50.00)
            )
        return insurance_id
    except Error as e:
        raise Exception(f"Query failed: {e}")

def get_refund_data(cursor, booking_id):
    try:
        cursor.execute("UPDATE Bookings SET status = 'Refunded' WHERE booking_id = %s", (booking_id,))
        return cursor.rowcount > 0
    except Error as e:
        raise Exception(f"Query failed: {e}")

def change_seat_data(cursor, booking_id, seat_number):
    try:
        cursor.execute("UPDATE Seats SET seat_number = %s WHERE booking_id = %s", (seat_number, booking_id))
        if cursor.rowcount == 0:
            return None
        cursor.execute("SELECT flight_number, seat_number, additional_fee FROM Seats WHERE booking_id = %s", (booking_id,))
        return cursor.fetchone()
    except Error as e:
        raise Exception(f"Query failed: {e}")

def cancel_trip_data(cursor, trip_id):
    try:
        cursor.execute("UPDATE Trips SET status = 'Cancelled' WHERE trip_id = %s", (trip_id,))
        return cursor.rowcount > 0
    except Error as e:
        raise Exception(f"Query failed: {e}")

def change_trip_data(cursor, trip_id, new_flight_number):
    try:
        cursor.execute(
            "UPDATE Trip_Components SET flight_number = %s WHERE trip_id = %s AND component_type = 'Flight'",
            (new_flight_number, trip_id)
        )
        if cursor.rowcount == 0:
            return None
        cursor.execute("SELECT component_type, flight_number, price FROM Trip_Components WHERE trip_id = %s", (trip_id,))
        return cursor.fetchone()
    except Error as e:
        raise Exception(f"Query failed: {e}")

def purchase_trip_insurance_data(cursor, trip_id):
    try:
        insurance_id = "INS" + str(hash(trip_id + "2025-06-03"))[:6]
        cursor.execute("SELECT insurance_id FROM Insurance WHERE insurance_id = %s", (insurance_id,))
        result = cursor.fetchone()
        if not result:        
            cursor.execute(
                "INSERT INTO Insurance (insurance_id, trip_id, coverage_type, coverage_amount, premium) "
                "VALUES (%s, %s, %s, %s, %s)",
                (insurance_id, trip_id, "Trip", 2000.00, 40.00)
            )
        return insurance_id
    except Error as e:
        raise Exception(f"Query failed: {e}")
    
    
#helper functions

def get_next_boarding_pass_id(cursor):
    cursor.execute("""
        SELECT boarding_pass_id
        FROM Boarding_Passes
        WHERE boarding_pass_id ~ '^BP[0-9]{3}$'
        ORDER BY boarding_pass_id DESC
        LIMIT 1;
    """)
    result = cursor.fetchone()
    if result:
        last_id = result[0]
        num = int(last_id[2:]) + 1
    else:
        num = 1
    return f"BP{num:03d}"

def get_booked_seat(cursor, booking_id, seat_number):
    try:
        cursor.execute(
            "SELECT seat_id, booking_id, flight_number, seat_number, additional_fee, currency "
            "FROM seats "
            "WHERE booking_id = %s AND seat_number = %s",
            (booking_id, seat_number)
        )
        result = cursor.fetchone()

        return result
    except Error as e:
        raise Exception(f"Query failed: {e}")