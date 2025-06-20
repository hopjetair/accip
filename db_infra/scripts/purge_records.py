import psycopg2
import os
import sys

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

def purge_all_records():
    # Prompt for confirmation to avoid accidental data loss
    confirmation = input("WARNING: This will delete ALL records from ALL tables in the 'public' schema. Type 'YES' to confirm: ")
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
    from datetime import datetime
    purge_all_records()