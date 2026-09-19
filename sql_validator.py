import re


# ============================================================
# APPROVED ANALYTICS VIEWS
# ============================================================

ALLOWED_VIEWS = {
    "public.v_customer_analytics",
    "public.v_order_analytics",
    "public.v_product_analytics",
    "public.v_revenue_analytics",
    "public.v_seller_analytics",
}


# ============================================================
# SQL VALIDATION FUNCTION
# ============================================================

def validate_sql(sql):

    # --------------------------------------------------------
    # 1. Empty query check
    # --------------------------------------------------------

    if not sql or not sql.strip():
        return False, "Empty SQL query."


    # --------------------------------------------------------
    # 2. Normalize SQL
    # --------------------------------------------------------

    normalized_sql = " ".join(sql.strip().split())

    # Remove one final semicolon
    normalized_sql = normalized_sql.rstrip(";").strip()


    # --------------------------------------------------------
    # 3. Only SELECT queries are allowed
    # --------------------------------------------------------

    if not re.match(
        r"^SELECT\b",
        normalized_sql,
        re.IGNORECASE
    ):
        return False, "Only SELECT queries are allowed."


    # --------------------------------------------------------
    # 4. Block dangerous SQL commands
    # --------------------------------------------------------

    forbidden_commands = [
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "GRANT",
        "REVOKE",
        "COPY",
        "VACUUM",
        "CALL",
        "DO",
        "EXECUTE",
        "MERGE",
        "COMMENT",
        "REFRESH",
    ]

    for command in forbidden_commands:

        pattern = rf"\b{command}\b"

        if re.search(
            pattern,
            normalized_sql,
            re.IGNORECASE
        ):
            return False, f"Forbidden SQL command detected: {command}"


    # --------------------------------------------------------
    # 5. Prevent multiple SQL statements
    # --------------------------------------------------------

    if ";" in normalized_sql:
        return False, "Multiple SQL statements are not allowed."


    # --------------------------------------------------------
    # 6. Block SQL comments
    # --------------------------------------------------------

    if "--" in normalized_sql:
        return False, "SQL comments are not allowed."

    if "/*" in normalized_sql or "*/" in normalized_sql:
        return False, "SQL comments are not allowed."


    # --------------------------------------------------------
    # 7. Block PostgreSQL system objects
    # --------------------------------------------------------

    dangerous_objects = [
        "information_schema",
        "pg_catalog",
        "pg_class",
        "pg_tables",
        "pg_user",
        "pg_roles",
        "pg_database",
        "pg_namespace",
    ]

    for obj in dangerous_objects:

        pattern = rf"\b{re.escape(obj)}\b"

        if re.search(
            pattern,
            normalized_sql,
            re.IGNORECASE
        ):
            return False, (
                f"Access to system objects is not allowed: {obj}"
            )


    # --------------------------------------------------------
    # 8. Find all FROM/JOIN sources
    # --------------------------------------------------------

    source_pattern = r"\b(?:FROM|JOIN)\s+([a-zA-Z_][\w]*(?:\.[a-zA-Z_][\w]*)?)"

    sources = re.findall(
        source_pattern,
        normalized_sql,
        re.IGNORECASE
    )


    # --------------------------------------------------------
    # 9. Make sure a data source exists
    # --------------------------------------------------------

    if not sources:
        return False, "No approved analytics view was found."


    # --------------------------------------------------------
    # 10. Every source must be approved
    # --------------------------------------------------------

    normalized_allowed_views = {
        view.lower()
        for view in ALLOWED_VIEWS
    }

    for source in sources:

        source_lower = source.lower()

        if source_lower not in normalized_allowed_views:

            return False, (
                f"Unauthorized table or view detected: {source}"
            )


    # --------------------------------------------------------
    # 11. Confirm at least one approved view exists
    # --------------------------------------------------------

    approved_found = any(
        source.lower() in normalized_allowed_views
        for source in sources
    )

    if not approved_found:
        return False, "Query does not use an approved analytics view."


    # --------------------------------------------------------
    # 12. Block dangerous PostgreSQL functions
    # --------------------------------------------------------

    dangerous_functions = [
        "pg_sleep",
        "pg_read_file",
        "pg_ls_dir",
        "pg_stat_file",
        "lo_import",
        "lo_export",
    ]

    for function in dangerous_functions:

        pattern = rf"\b{re.escape(function)}\s*\("

        if re.search(
            pattern,
            normalized_sql,
            re.IGNORECASE
        ):
            return False, (
                f"Dangerous PostgreSQL function detected: {function}"
            )


    # --------------------------------------------------------
    # 13. Validation successful
    # --------------------------------------------------------

    return True, "SQL is safe."