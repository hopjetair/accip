import psycopg2
import os
import sys
from datetime import datetime

# Add the parent directory to the Python path to find config.py if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    from config import db_host, db_port, db_name, db_user, db_pass
except ImportError:
    # Fallback to environment variables if config.py is not found
    db_host = os.getenv("DB_HOST", "database-1.c50k40mcme1j.ap-southeast-2.rds.amazonaws.com")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "hopjetairline_db")
    db_user = os.getenv("DB_USER", "dafa")
    db_pass = os.getenv("DB_PASS", "asdfasdfs!")

def verify_record_count():
    print(f"Starting record count verification at {datetime.now().strftime('%H:%M:%S')}")
    
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