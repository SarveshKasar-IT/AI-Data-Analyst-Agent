import re
import pandas as pd

from db import run_query


# Views that the AI analyst is allowed to query
ALLOWED_VIEWS = {
    "v_order_analytics",
    "v_customer_analytics",
    "v_product_analytics",
    "v_revenue_analytics",
    "v_seller_analytics",
}


def validate_sql(query: str) -> bool:
    """
    Validate SQL before sending it to PostgreSQL.
    Only analytical SELECT/WITH queries are allowed.
    """

    query = query.strip()

    # Must start with SELECT or WITH
    if not re.match(r"^(SELECT|WITH)\b", query, re.IGNORECASE):
        raise ValueError("Only SELECT or WITH queries are allowed.")

    # Block dangerous SQL operations
    blocked_keywords = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "GRANT",
        "REVOKE",
    ]

    for keyword in blocked_keywords:
        if re.search(rf"\b{keyword}\b", query, re.IGNORECASE):
            raise ValueError(
                f"Blocked SQL operation detected: {keyword}"
            )

    return True


def execute_safe_query(query: str) -> pd.DataFrame:
    """
    Validate and execute a read-only analytical SQL query.
    """

    validate_sql(query)

    return run_query(query)


if __name__ == "__main__":

    print("=" * 60)
    print("TESTING SAFE SQL EXECUTION")
    print("=" * 60)

    query = """
        SELECT
            product_category_name,
            ROUND(SUM(total_revenue)::numeric, 2) AS revenue
        FROM v_product_analytics
        GROUP BY product_category_name
        ORDER BY revenue DESC
        LIMIT 10;
    """

    df = execute_safe_query(query)

    print(df)

    print("=" * 60)
    print("SAFE SQL EXECUTION SUCCESSFUL")
    print("=" * 60)
