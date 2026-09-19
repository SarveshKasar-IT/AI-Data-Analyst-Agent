import os
import psycopg2
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def get_setting(name, default=None):
    """
    Read configuration from environment variables first.
    On Streamlit Cloud, fall back to Streamlit secrets.
    """

    value = os.getenv(name)

    if value:
        return value

    try:
        return st.secrets.get(name, default)
    except Exception:
        return default


DB_HOST = get_setting("DB_HOST", "localhost")
DB_NAME = get_setting("DB_NAME")
DB_USER = get_setting("DB_USER")
DB_PASSWORD = get_setting("DB_PASSWORD")
DB_PORT = get_setting("DB_PORT", "5432")


# Local PostgreSQL normally does not use SSL.
# Neon PostgreSQL requires SSL.
if DB_HOST in ("localhost", "127.0.0.1", "::1"):
    DB_SSLMODE = "disable"
else:
    DB_SSLMODE = "require"


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
            sslmode=DB_SSLMODE,
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