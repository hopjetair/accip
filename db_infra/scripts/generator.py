# generator.py
from datetime import datetime, timedelta
from faker import Faker
import random
import psycopg2
import os
from config import *

class DataGenerator:
    def __init__(self, host=os.getenv("DB_HOST", db_host), port=os.getenv("DB_PORT", db_port), 
                 db=os.getenv("DB_NAME", db_name), user=os.getenv("DB_USER", db_user), 
                 password=os.getenv("DB_PASS", db_pass)):
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

    # [Rest of the methods remain unchanged...]

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
        boarding_passes_count = bookings_count
        seats_count = bookings_count
        offers_count = flights_count + trips_count
        insurance_count = flights_count + trips_count
        print(f"Large dataset ({passengers_count + flights_count + bookings_count + boarding_passes_count + seats_count + trips_count + trip_components_count + offers_count + insurance_count}) records loaded into PostgreSQL successfully.")

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