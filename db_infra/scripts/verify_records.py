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


def verify_record_count():
    print(f"Starting record count verification at {datetime.now().strftime('%H:%M:%S')}")
    
    print(f"host : {os.getenv("db_host")}" )
    
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
            print("No tables found in the 'public' schema at {datetime.now().strftime('%H:%M:%S')}")
            return

        print(f"Found {len(tables)} tables in the 'public' schema: {', '.join(tables)}")
        total_count = 0

        # Count records for each table
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"Table {table} has {count} records at {datetime.now().strftime('%H:%M:%S')}")
                total_count += count
            except psycopg2.Error as e:
                print(f"Error counting records for table {table} at {datetime.now().strftime('%H:%M:%S')}: {e}")

        print(f"Total records across all tables: {total_count} at {datetime.now().strftime('%H:%M:%S')}")

    except psycopg2.Error as e:
        print(f"Database connection error at {datetime.now().strftime('%H:%M:%S')}: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
        print(f"Finished record count verification at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    verify_record_count()