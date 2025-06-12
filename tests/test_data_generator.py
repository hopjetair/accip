import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

import unittest
import psycopg2
from src.data.generator import DataGenerator
from datetime import datetime, timedelta

import os
from config import *
from src.utils.secretload import get_secret

get_secret(db_pass)


class TestDataGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        """Set up the test database and schema once for all tests."""
        # Connect to PostgreSQL and create the test database if needed
        try:
            conn = psycopg2.connect(
                host=db_host, port=db_port, user=db_user, password=os.getenv(db_pass)
            )
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE {db_testname};")
            cursor.close()
            conn.close()
        except psycopg2.errors.DuplicateDatabase:
            pass  # Database already exists

        # Apply the schema to test_airline_db (assumes create_airline_schema.sql exists)
        #import os
        #/os.system("psql -h localhost -p 5433 -U postgres -d test_airline_db -f create_airline_schema.sql")
        import os
        command = fr'"C:\Program Files\PostgreSQL\17\bin\psql" -h {db_host} -p {db_port} -U {db_user} -W {os.getenv(db_pass)} -d {db_testname}  -f create_airline_schema.sql'
        os.system(command)
        
    @classmethod
    def tearDownClass(cls):
        """Clean up by deleting the test database after all tests."""
        try:
            # Connect to the main PostgreSQL instance (not test_airline_db)
            conn = psycopg2.connect(
                host=db_host, port=db_port, user=db_user, password=os.getenv(db_pass)
            )
            conn.autocommit = True
            cursor = conn.cursor()

            # Drop the test database if it exists
            cursor.execute(f"DROP DATABASE IF EXISTS {db_testname};")
            cursor.close()
            conn.close()
        except psycopg2.Error as e:
            print(f"Warning: Failed to delete {db_testname}: {e}")        

    def setUp(self):
        """Set up the DataGenerator instance for each test."""
        self.generator = DataGenerator(db=db_testname)
        # Truncate all tables before each test to ensure a clean state
        self.generator.cursor.execute(
            "TRUNCATE TABLE Passengers, Flights, Bookings, Boarding_Passes, Trips, Trip_Components, Seats, Insurance, Offers RESTART IDENTITY CASCADE;"
        )
        self.generator.conn.commit()

    def tearDown(self):
        """Clean up after each test."""
        self.generator.conn.rollback()  # Roll back any uncommitted changes
        self.generator.close()

    def test_generate_passengers(self):
        """Test generating passenger records."""
        passengers = self.generator.generate_passengers(count=2)
        self.assertEqual(len(passengers), 2)
        self.generator.cursor.execute("SELECT COUNT(*) FROM Passengers")
        count = self.generator.cursor.fetchone()[0]
        self.assertEqual(count, 2)
        # Verify data integrity
        self.generator.cursor.execute("SELECT passenger_id FROM Passengers WHERE passenger_id = %s", (passengers[0],))
        self.assertIsNotNone(self.generator.cursor.fetchone())

    def test_generate_flights(self):
        """Test generating flight records."""
        flights = self.generator.generate_flights(count=2)
        self.assertEqual(len(flights), 2)
        self.generator.cursor.execute("SELECT COUNT(*) FROM Flights")
        count = self.generator.cursor.fetchone()[0]
        self.assertEqual(count, 2)
        # Verify data integrity
        self.generator.cursor.execute("SELECT flight_number FROM Flights WHERE flight_number = %s", (flights[0],))
        self.assertIsNotNone(self.generator.cursor.fetchone())

    def test_generate_bookings(self):
        """Test generating booking records."""
        passengers = self.generator.generate_passengers(count=2)
        flights = self.generator.generate_flights(count=2)
        bookings = self.generator.generate_bookings(count=3, passengers=passengers, flights=flights)
        self.assertEqual(len(bookings), 3)
        self.generator.cursor.execute("SELECT COUNT(*) FROM Bookings")
        count = self.generator.cursor.fetchone()[0]
        self.assertEqual(count, 3)
        # Verify data integrity: booking references existing passenger and flight
        self.generator.cursor.execute("SELECT passenger_id, flight_number FROM Bookings WHERE booking_id = %s", (bookings[0],))
        result = self.generator.cursor.fetchone()
        self.assertIn(result[0], passengers)
        self.assertIn(result[1], flights)

    def test_generate_boarding_passes(self):
        """Test generating boarding pass records."""
        passengers = self.generator.generate_passengers(count=2)
        flights = self.generator.generate_flights(count=2)
        bookings = self.generator.generate_bookings(count=3, passengers=passengers, flights=flights)
        self.generator.generate_boarding_passes(bookings=bookings)
        self.generator.cursor.execute("SELECT COUNT(*) FROM Boarding_Passes")
        count = self.generator.cursor.fetchone()[0]
        self.assertEqual(count, 3)
        # Verify data integrity: boarding pass references existing booking
        self.generator.cursor.execute("SELECT booking_id FROM Boarding_Passes WHERE boarding_pass_id = %s", ("BP001",))
        result = self.generator.cursor.fetchone()
        self.assertIn(result[0], bookings)

    def test_generate_trips(self):
        """Test generating trip records."""
        passengers = self.generator.generate_passengers(count=2)
        trips = self.generator.generate_trips(count=2, passengers=passengers)
        self.assertEqual(len(trips), 2)
        self.generator.cursor.execute("SELECT COUNT(*) FROM Trips")
        count = self.generator.cursor.fetchone()[0]
        self.assertEqual(count, 2)
        # Verify data integrity
        self.generator.cursor.execute("SELECT passenger_id FROM Trips WHERE trip_id = %s", (trips[0],))
        result = self.generator.cursor.fetchone()
        self.assertIn(result[0], passengers)

    def test_generate_trip_components(self):
        """Test generating trip component records."""
        passengers = self.generator.generate_passengers(count=2)
        flights = self.generator.generate_flights(count=2)
        trips = self.generator.generate_trips(count=2, passengers=passengers)
        self.generator.generate_trip_components(count=3, trips=trips, flights=flights)
        self.generator.cursor.execute("SELECT COUNT(*) FROM Trip_Components")
        count = self.generator.cursor.fetchone()[0]
        self.assertEqual(count, 3)
        # Verify data integrity
        self.generator.cursor.execute("SELECT trip_id, flight_number FROM Trip_Components LIMIT 1")
        result = self.generator.cursor.fetchone()
        self.assertIn(result[0], trips)
        self.assertIn(result[1], flights)

    def test_generate_seats(self):
        """Test generating seat records."""
        passengers = self.generator.generate_passengers(count=2)
        flights = self.generator.generate_flights(count=2)
        bookings = self.generator.generate_bookings(count=3, passengers=passengers, flights=flights)
        self.generator.generate_seats(bookings=bookings)
        self.generator.cursor.execute("SELECT COUNT(*) FROM Seats")
        count = self.generator.cursor.fetchone()[0]
        self.assertEqual(count, 3)
        # Verify data integrity
        self.generator.cursor.execute("SELECT booking_id FROM Seats LIMIT 1")
        result = self.generator.cursor.fetchone()
        self.assertIn(result[0], bookings)

    def test_generate_insurance(self):
        """Test generating insurance records."""
        passengers = self.generator.generate_passengers(count=2)
        flights = self.generator.generate_flights(count=2)
        bookings = self.generator.generate_bookings(count=3, passengers=passengers, flights=flights)
        trips = self.generator.generate_trips(count=2, passengers=passengers)
        self.generator.generate_insurance(flight_count=2, trip_count=2, bookings=bookings, trips=trips)
        self.generator.cursor.execute("SELECT COUNT(*) FROM Insurance")
        count = self.generator.cursor.fetchone()[0]
        self.assertEqual(count, 4)
        # Verify data integrity
        self.generator.cursor.execute("SELECT booking_id FROM Insurance WHERE coverage_type = 'Flight' LIMIT 1")
        result = self.generator.cursor.fetchone()
        self.assertIn(result[0], bookings)
        self.generator.cursor.execute("SELECT trip_id FROM Insurance WHERE coverage_type = 'Trip' LIMIT 1")
        result = self.generator.cursor.fetchone()
        self.assertIn(result[0], trips)

    def test_generate_offers(self):
        """Test generating offer records."""
        flights = self.generator.generate_flights(count=2)
        passengers = self.generator.generate_passengers(count=2)
        trips = self.generator.generate_trips(count=2, passengers=passengers)
        self.generator.generate_offers(flight_count=2, trip_count=2, flights=flights, trips=trips)
        self.generator.cursor.execute("SELECT COUNT(*) FROM Offers")
        count = self.generator.cursor.fetchone()[0]
        self.assertEqual(count, 4)
        # Verify data integrity
        self.generator.cursor.execute("SELECT flight_number FROM Offers WHERE offer_type = 'Flight' LIMIT 1")
        result = self.generator.cursor.fetchone()
        self.assertIn(result[0], flights)
        self.generator.cursor.execute("SELECT trip_id FROM Offers WHERE offer_type = 'Trip' LIMIT 1")
        result = self.generator.cursor.fetchone()
        self.assertIn(result[0], trips)

    def test_generate_dataset(self):
        """Test generating the complete dataset."""
        self.generator.generate_dataset(
            passengers_count=2, flights_count=2, bookings_count=3, trips_count=2, trip_components_count=3
        )
        self.generator.cursor.execute("SELECT COUNT(*) FROM Passengers")
        self.assertEqual(self.generator.cursor.fetchone()[0], 2)
        self.generator.cursor.execute("SELECT COUNT(*) FROM Flights")
        self.assertEqual(self.generator.cursor.fetchone()[0], 2)
        self.generator.cursor.execute("SELECT COUNT(*) FROM Bookings")
        self.assertEqual(self.generator.cursor.fetchone()[0], 3)
        self.generator.cursor.execute("SELECT COUNT(*) FROM Boarding_Passes")
        self.assertEqual(self.generator.cursor.fetchone()[0], 3)
        self.generator.cursor.execute("SELECT COUNT(*) FROM Trips")
        self.assertEqual(self.generator.cursor.fetchone()[0], 2)
        self.generator.cursor.execute("SELECT COUNT(*) FROM Trip_Components")
        self.assertEqual(self.generator.cursor.fetchone()[0], 3)
        self.generator.cursor.execute("SELECT COUNT(*) FROM Seats")
        self.assertEqual(self.generator.cursor.fetchone()[0], 3)
        self.generator.cursor.execute("SELECT COUNT(*) FROM Insurance")
        self.assertEqual(self.generator.cursor.fetchone()[0], 4)  # 2 flight + 2 trip
        self.generator.cursor.execute("SELECT COUNT(*) FROM Offers")
        self.assertEqual(self.generator.cursor.fetchone()[0], 4)  # 2 flight + 2 trip

if __name__ == "__main__":
    unittest.main()