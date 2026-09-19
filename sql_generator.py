import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-3.6-flash"


DATABASE_SCHEMA = """
You have access ONLY to these PostgreSQL analytics views.

==================================================
1. public.v_customer_analytics
==================================================
customer_id: text
total_orders: bigint
unique_products: bigint
total_product_value: double precision
total_freight_value: double precision
total_spend: double precision
average_item_value: double precision
first_purchase_date: timestamp
last_purchase_date: timestamp
delivered_orders: bigint
cancelled_orders: bigint
late_delivery_rate: numeric

Use this view for:
- customer analysis
- customer spending
- customer orders
- customer purchasing behavior
- customer delivery behavior
- customer cancellation behavior


==================================================
2. public.v_order_analytics
==================================================
order_id: text
customer_id: text
order_status: text
purchase_date: timestamp
approved_date: timestamp
delivered_to_carrier_date: timestamp
delivered_to_customer_date: timestamp
estimated_delivery_date: timestamp
product_id: text
product_category_name: text
seller_id: text
price: double precision
freight_value: double precision
item_total_value: double precision
delivery_duration: interval
is_late_delivery: integer

Use this view for:
- individual orders
- order status
- cancellations
- delivery time
- late deliveries
- order-level analysis
- product/order relationships
- seller/order relationships


==================================================
3. public.v_product_analytics
==================================================
product_id: text
product_category_name: text
total_orders: bigint
units_sold: bigint
number_of_sellers: bigint
total_product_revenue: double precision
total_freight_revenue: double precision
total_revenue: double precision
average_price: double precision
average_freight_value: double precision
minimum_price: double precision
maximum_price: double precision

Use this view for:
- product analysis
- product revenue
- best-selling products
- units sold
- product categories
- product pricing
- product performance


==================================================
4. public.v_revenue_analytics
==================================================
revenue_month: timestamp
total_orders: bigint
total_customers: bigint
product_revenue: double precision
freight_revenue: double precision
total_revenue: double precision
average_item_value: double precision
delivered_orders: bigint
cancelled_orders: bigint
late_delivery_rate: numeric

Use this view for:
- monthly revenue
- revenue trends
- sales trends
- total revenue
- monthly orders
- monthly customers
- monthly cancellations
- monthly delivery performance


==================================================
5. public.v_seller_analytics
==================================================
seller_id: text
total_orders: bigint
total_items_sold: bigint
unique_products: bigint
total_product_revenue: double precision
total_freight_revenue: double precision
total_revenue: double precision
average_product_price: double precision
average_freight_value: double precision
average_item_value: double precision

Use this view for:
- seller analysis
- seller revenue
- seller performance
- seller orders
- seller sales
- seller product performance
"""


def generate_sql(user_question):

    prompt = f"""
You are an expert PostgreSQL data analyst.

Your job is to convert the user's natural-language question
into ONE safe PostgreSQL SQL query.

DATABASE SCHEMA:
{DATABASE_SCHEMA}

USER QUESTION:
{user_question}

IMPORTANT RULES:

1. Generate ONLY SQL.
2. Do NOT include explanations.
3. Do NOT use markdown code fences.
4. ONLY generate SELECT statements.
5. WITH ... SELECT queries are allowed.
6. NEVER generate INSERT, UPDATE, DELETE, DROP, ALTER,
   CREATE, TRUNCATE, GRANT, REVOKE, or other write operations.
7. ONLY use the five views listed in the database schema.
8. NEVER invent tables, views, or columns.
9. Choose the view that best matches the user's question.
10. Do NOT join views unless a join is genuinely necessary.
11. Prefer the simplest correct query.
12. For "top N", use ORDER BY ... DESC and LIMIT N.
13. For descending numeric ordering, use NULLS LAST.
14. For customer spending, use total_spend.
15. For customer orders, use total_orders.
16. For products sold by a customer, use unique_products.
17. For product revenue, use total_product_revenue or total_revenue
    depending on the question.
18. For seller revenue, use total_revenue.
19. For monthly revenue, use v_revenue_analytics.
20. For late delivery rate, use late_delivery_rate.
21. If the question asks for a percentage, calculate it correctly.
22. If the question asks for a count, use COUNT where appropriate.
23. If the question asks for an average, use AVG where appropriate.
24. Always use fully qualified view names such as:
    public.v_customer_analytics
25. Return one executable SQL statement ending with a semicolon.

Now generate the SQL.
"""

    response = client.interactions.create(
        model=MODEL_NAME,
        input=prompt
    )

    # Current Gemini Interactions API response format
    sql = response.output_text.strip()

    # Remove markdown code fences if Gemini accidentally adds them
    sql = sql.replace("```sql", "").replace("```", "").strip()

    return sql


if __name__ == "__main__":

    print("\nAI SQL Generator")
    print("Type 'exit' to quit.")

    while True:

        question = input("\nEnter your question: ")

        if question.lower().strip() == "exit":
            print("\nGoodbye!")
            break

        if not question.strip():
            print("Please enter a question.")
            continue

        try:

            sql = generate_sql(question)

            print("\nGenerated SQL:")
            print(sql)

        except Exception as e:

            print(f"\nError: {e}")