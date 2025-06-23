import psycopg2
import os
import sys
from datetime import datetime

# Add the parent directory to the Python path to find config.py if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config import *
from src.utils.secretload import get_secret

if len(sys.argv) > 1:  # than it is assumed it for localhost
    os.environ["db_host"] = const_localhost # "localhost"
    
    os.environ["db_user"] = const_db_user #  "hopjetair"  # user for the database
    os.environ["db_pass"] = const_db_pass # "SecurePass123!"  # password for the databaser
else:
    os.environ["db_host"] = const_cloudhost  
    get_secret("db_credentials")    

def purge_all_records():
    # Prompt for confirmation to avoid accidental data loss
    confirmation = input(f"WARNING: This will delete ALL records from ALL tables in the 'public' schema for host {db_host}. Type 'YES' to confirm: ")
    if confirmation.upper() != "YES":
        print("Operation cancelled by user.")
        return

    # Establish database connection
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_pass
        )
        cursor = conn.cursor()

        # Get all tables in the public schema
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            print("No tables found in the 'public' schema.")
            return

        print(f"Found {len(tables)} tables in the 'public' schema: {', '.join(tables)}")
        print(f"Starting to purge records at {datetime.now().strftime('%H:%M:%S')}")

        # Truncate all tables with CASCADE to handle foreign keys
        for table in tables:
            try:
                cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
                print(f"Purged records from table {table} at {datetime.now().strftime('%H:%M:%S')}")
            except psycopg2.Error as e:
                print(f"Error purging table {table} at {datetime.now().strftime('%H:%M:%S')}: {e}")
                conn.rollback()
                return

        # Commit the transaction
        conn.commit()
        print(f"Finished purging all records at {datetime.now().strftime('%H:%M:%S')}")

    except psycopg2.Error as e:
        print(f"Database connection error at {datetime.now().strftime('%H:%M:%S')}: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print(f"Database connection closed at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    purge_all_records()