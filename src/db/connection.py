# connection.py
import psycopg2
from psycopg2 import Error
import os
from config import *

def get_db_connection():
    """Establish a connection to the PostgreSQL database."""
    try:
        print(f"Host :  {db_host}" )
        conn = psycopg2.connect(
            host=os.getenv(const_fieldname_db_host, db_host),
            port=os.getenv(const_fieldname_db_port, db_port),
            database=os.getenv(const_fieldname_db_name, db_name),
            user=os.getenv(const_fieldname_db_user, db_user),
            password=os.getenv(const_fieldname_db_pass, db_pass)
        )
        return conn
    except Error as e:
        raise Exception(f"Database connection failed: {e}")