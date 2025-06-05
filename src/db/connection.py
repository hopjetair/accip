import psycopg2

def get_db_connection():
    """Return a database connection to airline_db."""
    return psycopg2.connect(
        host="localhost", port=5433, database="airline_db", user="postgres", password="Testing!@123"
    )