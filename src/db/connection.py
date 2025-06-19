# connection.py
import psycopg2
from psycopg2 import Error
import os
from config import *

def get_db_connection():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_pass
        )
        return conn
    except Error as e:
        raise Exception(f"Database connection failed: {e}")