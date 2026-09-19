import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")


def execute_query(sql):
    connection = None
    cursor = None

    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            sslmode="require",
            connect_timeout=15
        )

        cursor = connection.cursor()

        cursor.execute(sql)

        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        return columns, rows

    except Exception as e:
        print(f"Database error: {type(e).__name__}: {e}")
        return None, None

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()