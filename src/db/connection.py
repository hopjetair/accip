import psycopg2
from psycopg2 import Error

def get_db_connection():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="airline_db",
            user="postgres",
            password="Testing!@123"
        )
        return conn
    except Error as e:
        raise Exception(f"Database connection failed: {e}")
    
    
    