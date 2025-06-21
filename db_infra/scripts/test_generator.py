import unittest
import os
import sys
from datetime import datetime
import psycopg2
from unittest.mock import patch

# Add the current directory and parent directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Add db_infra/scripts/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))  # Add project root

from .generator import DataGenerator

class TestDataGenerator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="postgres",
            user="postgres",
            password="Testing!@123"
        )
        cls.cursor = cls.conn.cursor()
        cls.test_db = "test_hopjetairline_db"
        try:
            cls.conn.autocommit = True
            cls.cursor.execute(f"DROP DATABASE IF EXISTS {cls.test_db}")
            cls.cursor.execute(f"CREATE DATABASE {cls.test_db}")
            cls.conn.autocommit = False
        except psycopg2.Error as e:
            cls.conn.rollback()
            raise Exception(f"Failed to set up test database: {e}")
        finally:
            cls.cursor.close()
            cls.conn.close()

    def setUp(self):
        self.conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database=self.test_db,
            user="postgres",
            password="Testing!@123"
        )
        self.cursor = self.conn.cursor()
        # Drop all tables to ensure a clean slate
        tables = ['passengers', 'flights', 'bookings', 'boarding_passes', 'trips',
                  'trip_components', 'seats', 'insurance', 'offers']
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        self.conn.commit()
        self.generator = DataGenerator(
            host="localhost",
            port="5432",
            db=self.test_db,
            user="postgres",
            password="Testing!@123"
        )
        self.generator.conn = self.conn
        self.generator.cursor = self.cursor

    def tearDown(self):
        self.cursor.close()
        self.conn.close()
        self.generator.close()

    @classmethod
    def tearDownClass(cls):
        cls.conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="postgres",
            user="postgres",
            password="Testing!@123"
        )
        cls.cursor = cls.conn.cursor()
        cls.conn.autocommit = True
        cls.cursor.execute(f"DROP DATABASE IF EXISTS {cls.test_db}")
        cls.conn.commit()
        cls.cursor.close()
        cls.conn.close()

    def test_database_creation(self):
        self.assertIsNotNone(self.generator.conn)
        self.assertEqual(self.generator.conn.status, psycopg2.extensions.STATUS_READY)

    def test_apply_schema_if_needed_new_table(self):
        self.generator.apply_schema_if_needed()
        self.cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'passengers'")
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 1)
        self.cursor.execute("SELECT COUNT(*) FROM passengers")
        count = self.cursor.fetchone()[0]
        self.assertEqual(count, 0)

    def test_apply_schema_if_needed_existing_table(self):
        self.cursor.execute("CREATE TABLE passengers (passenger_id VARCHAR(10) PRIMARY KEY, name VARCHAR(100) NOT NULL, email VARCHAR(100), phone VARCHAR(20), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        self.conn.commit()
        with patch('builtins.open', return_value=MockFile(['CREATE TABLE passengers (passenger_id VARCHAR(10) PRIMARY KEY, name VARCHAR(100) NOT NULL, email VARCHAR(100), phone VARCHAR(20), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);'])):
            with self.assertLogs(level='INFO') as cm:
                self.generator.apply_schema_if_needed()
            self.cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'passengers'")
            count = self.cursor.fetchone()[0]
            self.assertEqual(count, 1)
            with self.assertRaises(psycopg2.Error):
                self.cursor.execute("CREATE TABLE passengers (passenger_id VARCHAR(10) PRIMARY KEY, name VARCHAR(100) NOT NULL)")
            self.assertIn("Schema for table passengers already exists", ''.join(cm.output))

    def test_apply_schema_if_needed_existing_index(self):
        self.cursor.execute("CREATE TABLE bookings (booking_id VARCHAR(10) PRIMARY KEY, passenger_id VARCHAR(10) NOT NULL, flight_number VARCHAR(10) NOT NULL, booking_date DATE NOT NULL, status VARCHAR(20) DEFAULT 'Confirmed', total_price DECIMAL(10, 2) NOT NULL, currency VARCHAR(3) DEFAULT 'USD', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        self.cursor.execute("CREATE INDEX idx_bookings_passenger_id ON bookings (passenger_id)")
        self.conn.commit()
        with open("db_infra/scripts/create_airline_schema.sql", 'r') as file:
            sql_script = file.read()
            statements = sql_script.split(';')
            sql_statements = [s for s in statements if s.strip() and not s.strip().startswith("import")]
            for statement in sql_statements:
                if "CREATE INDEX idx_bookings_passenger_id" in statement:
                    with self.assertLogs(level='INFO') as cm:
                        self.generator.apply_schema_if_needed()
                    self.assertIn("Index idx_bookings_passenger_id already exists", ''.join(cm.output))

    def test_apply_schema_if_needed_new_index(self):
        self.cursor.execute("CREATE TABLE bookings (booking_id VARCHAR(10) PRIMARY KEY, passenger_id VARCHAR(10) NOT NULL, flight_number VARCHAR(10) NOT NULL, booking_date DATE NOT NULL, status VARCHAR(20) DEFAULT 'Confirmed', total_price DECIMAL(10, 2) NOT NULL, currency VARCHAR(3) DEFAULT 'USD', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        self.conn.commit()
        with open("db_infra/scripts/create_airline_schema.sql", 'r') as file:
            sql_script = file.read()
            statements = sql_script.split(';')
            sql_statements = [s for s in statements if s.strip() and not s.strip().startswith("import")]
            for statement in sql_statements:
                if "CREATE INDEX idx_bookings_passenger_id" in statement:
                    with self.assertLogs(level='INFO') as cm:
                        self.generator.apply_schema_if_needed()
                    self.assertIn("Creating index for idx_bookings_passenger_id", ''.join(cm.output))
                    self.cursor.execute("SELECT 1 FROM pg_indexes WHERE indexname = 'idx_bookings_passenger_id'")
                    self.assertIsNotNone(self.cursor.fetchone())

    def test_generate_dataset(self):
        self.generator.apply_schema_if_needed()
        required_tables = ['passengers', 'flights', 'bookings', 'boarding_passes', 'trips',
                          'trip_components', 'seats', 'insurance', 'offers']
        existing_tables = []
        self.cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        for row in self.cursor.fetchall():
            existing_tables.append(row[0].lower())
        if all(table in existing_tables for table in required_tables):
            self.generator.generate_dataset(passengers_count=2, flights_count=1, bookings_count=2)
            self.cursor.execute("SELECT COUNT(*) FROM passengers")
            passengers_count = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT COUNT(*) FROM flights")
            flights_count = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT COUNT(*) FROM bookings")
            bookings_count = self.cursor.fetchone()[0]
            self.assertEqual(passengers_count, 2)
            self.assertEqual(flights_count, 1)
            self.assertEqual(bookings_count, 2)
        else:
            self.fail("Schema application failed; required tables are missing")

class MockFile:
    def __init__(self, lines):
        self.lines = lines
    def read(self):
        return ';'.join(self.lines)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

if __name__ == '__main__':
    unittest.main()