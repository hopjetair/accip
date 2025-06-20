import psycopg2

db_host = "database-1.c50k40mcme1j.ap-southeast-2.rds.amazonaws.com"
db_name = "hopjetairline_db"
db_user = "hopjetair"
db_pass = "SecurePass123!"

connection = psycopg2.connect(host = db_host, database =  db_name, user = db_user, password = db_pass)
print("connected to the databaser")

cursor = connection.cursor()
cursor.execute("Select 1")
db_version = cursor.fetchone()
print(db_version)
# Query visible tables
cursor.execute("""
    SELECT tablename, schemaname 
    FROM pg_catalog.pg_tables 
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
""")

tables = cursor.fetchall()

# Display table names
for tablename, schemaname in tables:
    print(f"{schemaname}.{tablename}")
    
    
# Query estimated row count per table
cursor.execute("""
    SELECT relname AS table_name, n_live_tup AS row_count
    FROM pg_stat_user_tables
    ORDER BY n_live_tup DESC;
""")

rows = cursor.fetchall()

# Print row counts table by table
print("📊 Estimated row counts per table:")
for table_name, row_count in rows:
    print(f"{table_name}: {row_count} rows")


cursor.close()