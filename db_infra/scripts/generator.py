from datetime import datetime, timedelta
from faker import Faker
import random
import psycopg2
import os
from config import *
from src.utils.secretload import get_secret

get_secret(db_pass)

class DataGenerator:
    def __init__(self, host=db_host, port=db_port, db=db_name, user=db_user, password=os.getenv(db_pass)):
        """Initialize the DataGenerator with database connection and helper data."""
        self.fake = Faker()
        self.conn = psycopg2.connect(
            host=host, port=port, database=db, user=user, password=password
        )
        self.cursor = self.conn.cursor()
        self.airports = [
            "Singapore (SIN)", "Sydney (SYD)", "Frankfurt (FRA)", "Paris (CDG)", "Tokyo (NRT)",
            "New York (JFK)", "London (LHR)", "Dubai (DXB)", "Los Angeles (LAX)", "Hong Kong (HKG)"
        ]
        self.gates = ["A12", "B5", "C3", "D10", "E7", "F15", "G8", "H2", "J4", "K11"]
        self.statuses = ["On Time", "Delayed", "Cancelled", "Boarding"]
        self.offer_types = ["Flight", "Trip"]

    def generate_passengers(self, count=200):
        """Generate a specified number of passenger records."""
        passengers = []
        for i in range(1, count + 1):
            passenger_id = f"P{i:03d}"
            name = self.fake.name()
            email = self.fake.email()
            phone = self.fake.phone_number()[:15]
            self.cursor.execute(
                "INSERT INTO Passengers (passenger_id, name, email, phone) VALUES (%s, %s, %s, %s)",
                (passenger_id, name, email, phone)
            )
            passengers.append(passenger_id)
        return passengers

    def generate_flights(self, count=50):
        """Generate a specified number of flight records."""
        flights = []
        for i in range(1, count + 1):
            flight_number = f"F{i:03d}"
            departure = random.choice(self.airports)
            destination = random.choice([a for a in self.airports if a != departure])
            departure_date = self.fake.date_between_dates(date_start=datetime(2025, 6, 1), date_end=datetime(2025, 12, 31))
            departure_time = datetime.combine(departure_date, datetime.strptime(random.choice(["09:00", "12:00", "15:00", "18:00"]), "%H:%M").time())
            flight_duration = timedelta(hours=random.randint(2, 15))
            arrival_time = departure_time + flight_duration
            gate = random.choice(self.gates)
            status = random.choice(self.statuses)
            price = round(random.uniform(100, 1000), 2)
            availability = random.randint(0, 20)
            self.cursor.execute(
                "INSERT INTO Flights (flight_number, departure, destination, departure_time, arrival_time, gate, status, price, availability) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (flight_number, departure, destination, departure_time, arrival_time, gate, status, price, availability)
            )
            flights.append(flight_number)
        return flights

    def generate_bookings(self, count=300, passengers=None, flights=None):
        """Generate a specified number of booking records."""
        bookings = []
        passengers = passengers or self.generate_passengers(count=200)
        flights = flights or self.generate_flights(count=50)
        for i in range(1, count + 1):
            booking_id = f"B{i:06d}"
            passenger_id = random.choice(passengers)
            flight_number = random.choice(flights)
            self.cursor.execute("SELECT price FROM Flights WHERE flight_number = %s", (flight_number,))
            price = self.cursor.fetchone()[0]
            booking_date = self.fake.date_between_dates(date_start=datetime(2025, 1, 1), date_end=datetime(2025, 6, 3))
            status = "Confirmed"
            self.cursor.execute(
                "INSERT INTO Bookings (booking_id, passenger_id, flight_number, booking_date, status, total_price) VALUES (%s, %s, %s, %s, %s, %s)",
                (booking_id, passenger_id, flight_number, booking_date, status, price)
            )
            bookings.append(booking_id)
        return bookings

    def generate_boarding_passes(self, bookings=None):
        """Generate boarding pass records for existing bookings."""
        bookings = bookings or self.generate_bookings(count=300)
        for i, booking_id in enumerate(bookings, 1):
            boarding_pass_id = f"BP{i:03d}"
            self.cursor.execute("SELECT flight_number FROM Bookings WHERE booking_id = %s", (booking_id,))
            flight_number = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT gate, departure_time FROM Flights WHERE flight_number = %s", (flight_number,))
            flight_info = self.cursor.fetchone()
            gate = flight_info[0]
            departure_time = flight_info[1]
            boarding_time = departure_time - timedelta(minutes=30)
            seat = f"{random.randint(1, 30)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}"
            pdf_url = f"https://airline.com/boardingpass/{booking_id}.pdf"
            self.cursor.execute(
                "INSERT INTO Boarding_Passes (boarding_pass_id, booking_id, gate, seat, boarding_time, pdf_url) VALUES (%s, %s, %s, %s, %s, %s)",
                (boarding_pass_id, booking_id, gate, seat, boarding_time, pdf_url)
            )

    def generate_trips(self, count=100, passengers=None):
        """Generate a specified number of trip records."""
        trips = []
        passengers = passengers or self.generate_passengers(count=200)
        for i in range(1, count + 1):
            trip_id = f"T{i:06d}"
            passenger_id = random.choice(passengers)
            total_price = round(random.uniform(500, 3000), 2)
            self.cursor.execute(
                "INSERT INTO Trips (trip_id, passenger_id, total_price) VALUES (%s, %s, %s)",
                (trip_id, passenger_id, total_price)
            )
            trips.append(trip_id)
        return trips

    def generate_trip_components(self, count=150, trips=None, flights=None):
        """Generate a specified number of trip component records."""
        trips = trips or self.generate_trips(count=100)
        flights = flights or self.generate_flights(count=50)
        for i in range(1, count + 1):
            trip_id = random.choice(trips)
            component_type = "Flight"
            flight_number = random.choice(flights)
            self.cursor.execute("SELECT price FROM Flights WHERE flight_number = %s", (flight_number,))
            price = self.cursor.fetchone()[0]
            self.cursor.execute(
                "INSERT INTO Trip_Components (trip_id, component_type, flight_number, hotel_name, check_in_date, check_out_date, price) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (trip_id, component_type, flight_number, None, None, None, price)
            )

    def generate_seats(self, bookings=None):
        """Generate seat records for existing bookings."""
        bookings = bookings or self.generate_bookings(count=300)
        for i, booking_id in enumerate(bookings, 1):
            self.cursor.execute("SELECT flight_number FROM Bookings WHERE booking_id = %s", (booking_id,))
            flight_number = self.cursor.fetchone()[0]
            seat_number = f"{random.randint(1, 30)}{random.choice(['A', 'B', 'C', 'D', 'E', 'F'])}"
            additional_fee = round(random.uniform(0, 50), 2)
            self.cursor.execute(
                "INSERT INTO Seats (booking_id, flight_number, seat_number, additional_fee) VALUES (%s, %s, %s, %s)",
                (booking_id, flight_number, seat_number, additional_fee)
            )

    def generate_insurance(self, flight_count=50, trip_count=50, bookings=None, trips=None):
        """Generate insurance records for flights and trips."""
        bookings = bookings or self.generate_bookings(count=300)
        trips = trips or self.generate_trips(count=100)
        for i in range(1, flight_count + 1):
            insurance_id = f"INS{i:03d}"
            booking_id = random.choice(bookings)
            self.cursor.execute("SELECT total_price FROM Bookings WHERE booking_id = %s", (booking_id,))
            coverage_amount = float(self.cursor.fetchone()[0])
            coverage_type = "Flight"
            premium = round(coverage_amount * 0.05, 2)
            self.cursor.execute(
                "INSERT INTO Insurance (insurance_id, booking_id, coverage_type, coverage_amount, premium) VALUES (%s, %s, %s, %s, %s)",
                (insurance_id, booking_id, coverage_type, coverage_amount, premium)
            )
        for i in range(flight_count + 1, flight_count + trip_count + 1):
            insurance_id = f"INS{i:03d}"
            trip_id = random.choice(trips)
            self.cursor.execute("SELECT total_price FROM Trips WHERE trip_id = %s", (trip_id,))
            coverage_amount = float(self.cursor.fetchone()[0])
            coverage_type = "Trip"
            premium = round(coverage_amount * 0.05, 2)
            self.cursor.execute(
                "INSERT INTO Insurance (insurance_id, trip_id, coverage_type, coverage_amount, premium) VALUES (%s, %s, %s, %s, %s)",
                (insurance_id, trip_id, coverage_type, coverage_amount, premium)
            )

    def generate_offers(self, flight_count=25, trip_count=25, flights=None, trips=None):
        """Generate offer records for flights and trips."""
        flights = flights or self.generate_flights(count=50)
        trips = trips or self.generate_trips(count=100)
        for i in range(1, flight_count + 1):
            offer_id = f"O{i:03d}"
            offer_type = "Flight"
            flight_number = random.choice(flights)
            self.cursor.execute("SELECT price FROM Flights WHERE flight_number = %s", (flight_number,))
            original_price = float(self.cursor.fetchone()[0])
            discount = random.choice(["10%", "15%", "20%"])
            discount_value = float(discount.strip("%")) / 100
            price = round(original_price * (1 - discount_value), 2)
            description = f"{discount} off {flight_number}"
            self.cursor.execute(
                "INSERT INTO Offers (offer_id, offer_type, flight_number, description, price, discount) VALUES (%s, %s, %s, %s, %s, %s)",
                (offer_id, offer_type, flight_number, description, price, discount)
            )
        for i in range(flight_count + 1, flight_count + trip_count + 1):
            offer_id = f"O{i:03d}"
            offer_type = "Trip"
            trip_id = random.choice(trips)
            self.cursor.execute("SELECT total_price FROM Trips WHERE trip_id = %s", (trip_id,))
            original_price = float(self.cursor.fetchone()[0])
            discount = random.choice(["10%", "15%", "20%"])
            discount_value = float(discount.strip("%")) / 100
            price = round(original_price * (1 - discount_value), 2)
            description = f"{discount} off trip {trip_id}"
            self.cursor.execute(
                "INSERT INTO Offers (offer_id, offer_type, trip_id, description, price, discount) VALUES (%s, %s, %s, %s, %s, %s)",
                (offer_id, offer_type, trip_id, description, price, discount)
            )

    def generate_dataset(self, passengers_count=200, flights_count=50, bookings_count=300, trips_count=100, trip_components_count=150):
        """Generate the complete dataset with specified counts."""
        passengers = self.generate_passengers(count=passengers_count)
        flights = self.generate_flights(count=flights_count)
        bookings = self.generate_bookings(count=bookings_count, passengers=passengers, flights=flights)
        self.generate_boarding_passes(bookings=bookings)
        trips = self.generate_trips(count=trips_count, passengers=passengers)
        self.generate_trip_components(count=trip_components_count, trips=trips, flights=flights)
        self.generate_seats(bookings=bookings)
        self.generate_insurance(flight_count=flights_count, trip_count=trips_count, bookings=bookings, trips=trips)
        self.generate_offers(flight_count=flights_count, trip_count=trips_count, flights=flights, trips=trips)
        
        self.conn.commit()
        boarding_passes_count =bookings_count
        seats_count = bookings_count
        offers_count = flights_count + trips_count
        insurance_count = flights_count + trips_count
        print(f"Large dataset ({passengers_count + flights_count + bookings_count +boarding_passes_count +seats_count + trips_count + trip_components_count + offers_count + insurance_count}) records loaded into PostgreSQL successfully.")

    def close(self):
        """Close the database connection."""
        self.cursor.close()
        self.conn.close()

if __name__ == "__main__":
    generator = DataGenerator()
    try:
        generator.generate_dataset()
    except Exception as e:
        print(f"Error: {e}")
        generator.conn.rollback()
    finally:
        generator.close()