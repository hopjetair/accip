import psycopg2
from psycopg2 import Error
import os
from config import *
from src.utils.secretload import get_secret

get_secret(db_pass)

def get_db_connection():
    """Establish a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=os.getenv(db_pass)
        )
        return conn
    except Error as e:
        raise Exception(f"Database connection failed: {e}")
    
    
    