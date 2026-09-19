import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT", "5432")
)

cursor = conn.cursor()

views = [
    "v_customer_analytics",
    "v_order_analytics",
    "v_product_analytics",
    "v_revenue_analytics",
    "v_seller_analytics"
]

for view in views:

    print("\n" + "=" * 60)
    print(f"VIEW: public.{view}")
    print("=" * 60)

    cursor.execute("""
        SELECT
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = %s
        ORDER BY ordinal_position;
    """, (view,))

    columns = cursor.fetchall()

    for column_name, data_type in columns:
        print(f"{column_name:35} {data_type}")

cursor.close()
conn.close()