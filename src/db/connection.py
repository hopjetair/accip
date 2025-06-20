# connection.py
import psycopg2
from psycopg2 import Error
import os
from config import *

def get_db_connection():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("db_host", db_host),
            port=os.getenv("db_port", db_port),
            database=os.getenv("db_name", db_name),
            user=os.getenv("db_user", db_user),
            password=os.getenv("db_pass", db_pass)
        )
        return conn
    except Error as e:
        raise Exception(f"Database connection failed: {e}")