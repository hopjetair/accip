import psycopg2

db_host = "database-1.c50k40mcme1j.ap-southeast-2.rds.amazonaws.com"
db_name = "hopjetairline_db"
db_user = "hopjetair"
db_pass = "SecurePass123!"

connection = psycopg2.connect(host = db_host, database =  db_name, user = db_user, password = db_pass)
print("connected to the databaser")

cursor = connection.cursor()
cursor.execute("Select version()")
db_version = cursor.fetchone()
print(db_version)

cursor.close()