from dotenv import load_dotenv
import os
import psycopg2

load_dotenv()

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
database = os.getenv("DB_NAME")

print("Database:", database)
print("Host:", host)
print("Port:", port)

try:
    conn = psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )

    print("DATABASE CONNECTION: SUCCESS")

    cursor = conn.cursor()
    cursor.execute("SELECT current_database();")

    print("Connected database:", cursor.fetchone()[0])

    cursor.close()
    conn.close()

except Exception as e:
    print("DATABASE CONNECTION: FAILED")
    print(type(e).__name__)
    print(e)