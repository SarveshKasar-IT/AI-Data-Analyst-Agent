import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# --------------------------------------------------
# 2. Create PostgreSQL connection
# --------------------------------------------------

connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME
)

engine = create_engine(connection_url)

# --------------------------------------------------
# 3. Dataset configuration
# --------------------------------------------------

DATA_DIR = os.path.join("data", "raw")

datasets = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "product_category_translation": "product_category_name_translation.csv"
}

# --------------------------------------------------
# 4. Load datasets into PostgreSQL
# --------------------------------------------------

print("\n============================================")
print("STARTING OLIST DATA INGESTION")
print("============================================\n")

for table_name, filename in datasets.items():

    file_path = os.path.join(DATA_DIR, filename)

    print(f"Loading: {filename}")

    try:
        df = pd.read_csv(file_path)

        print(f"Rows found: {len(df):,}")
        print(f"Columns: {len(df.columns)}")

        df.to_sql(
            table_name,
            engine,
            if_exists="replace",
            index=False,
            method="multi",
            chunksize=5000
        )

        print(f"✓ Loaded into PostgreSQL table: {table_name}\n")

    except Exception as e:
        print(f"✗ Failed: {filename}")
        print(f"Error: {e}\n")

# --------------------------------------------------
# 5. Validate row counts
# --------------------------------------------------

print("\n============================================")
print("POSTGRESQL ROW COUNT VALIDATION")
print("============================================\n")

with engine.connect() as conn:

    for table_name in datasets.keys():

        result = conn.execute(
            text(f'SELECT COUNT(*) FROM "{table_name}"')
        )

        count = result.scalar()

        print(f"{table_name:<35} {count:>10,}")

print("\n============================================")
print("DATA INGESTION COMPLETED")
print("============================================")