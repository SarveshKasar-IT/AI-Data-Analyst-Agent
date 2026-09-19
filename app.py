import io
import csv
import pandas as pd
import plotly.express as px
import streamlit as st

from sql_generator import generate_sql
from sql_validator import validate_sql
from query_executor import execute_query
from answer_generator import generate_answer


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Data Analyst Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 2.4rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        font-size: 1rem;
        color: #666666;
        margin-bottom: 1.5rem;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 650;
        margin-top: 1rem;
        margin-bottom: 0.7rem;
    }

    .pipeline {
        padding: 0.8rem 1rem;
        border-radius: 10px;
        background-color: #f5f5f5;
        margin-bottom: 1.2rem;
        font-size: 0.95rem;
    }

    .success-box {
        padding: 0.7rem 1rem;
        border-radius: 8px;
        background-color: #f0f8f0;
        border: 1px solid #b8d8b8;
    }

    .warning-box {
        padding: 0.7rem 1rem;
        border-radius: 8px;
        background-color: #fff8e6;
        border: 1px solid #e5c97a;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "query_history" not in st.session_state:
    st.session_state.query_history = []


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def pretty_name(column_name):
    """
    Convert database column names into readable labels.
    Example:
        total_revenue -> Total Revenue
        cancelled_orders -> Cancelled Orders
    """

    name = str(column_name)

    name = name.replace("_", " ")
    name = name.replace("-", " ")

    return name.strip().title()


def is_currency_column(column_name):
    """
    Detect monetary/revenue-related columns.
    """

    column = str(column_name).lower()

    currency_keywords = [
        "revenue",
        "spend",
        "price",
        "freight",
        "monetary",
        "product_value",
        "total_value",
        "item_value",
        "average_price",
        "minimum_price",
        "maximum_price"
    ]

    return any(keyword in column for keyword in currency_keywords)


def is_count_column(column_name):
    """
    Detect count-related columns.
    """

    column = str(column_name).lower()

    count_keywords = [
        "orders",
        "order_count",
        "customers",
        "customer_count",
        "cancelled",
        "canceled",
        "units",
        "items",
        "sellers",
        "products",
        "total_orders",
        "total_customers"
    ]

    return any(keyword in column for keyword in count_keywords)


def is_rate_column(column_name):
    """
    Detect percentage/rate columns.
    """

    column = str(column_name).lower()

    rate_keywords = [
        "rate",
        "percentage",
        "percent",
        "ratio"
    ]

    return any(keyword in column for keyword in rate_keywords)


def format_brazilian_currency(value):
    """
    Format number using Brazilian currency notation.

    Example:
        1234567.89
        -> R$ 1.234.567,89
    """

    try:
        number = float(value)

        formatted = f"{number:,.2f}"

        formatted = (
            formatted
            .replace(",", "TEMP")
            .replace(".", ",")
            .replace("TEMP", ".")
        )

        return f"R$ {formatted}"

    except (ValueError, TypeError):
        return str(value)


def format_number(value, column_name):
    """
    Format values according to their meaning.
    """

    if pd.isna(value):
        return ""

    column = str(column_name).lower()

    # --------------------------------------------------------
    # Currency
    # --------------------------------------------------------

    if is_currency_column(column):
        return format_brazilian_currency(value)

    # --------------------------------------------------------
    # Integer/count values
    # --------------------------------------------------------

    if is_count_column(column):
        try:
            return f"{int(round(float(value))):,}"
        except (ValueError, TypeError):
            return str(value)

    # --------------------------------------------------------
    # Percentage/rate values
    # --------------------------------------------------------

    if is_rate_column(column):
        try:
            number = float(value)

            # If database already stores 0.25,
            # display 25.00%.
            if abs(number) <= 1:
                number *= 100

            return f"{number:.2f}%"

        except (ValueError, TypeError):
            return str(value)

    # --------------------------------------------------------
    # General numeric value
    # --------------------------------------------------------

    if isinstance(value, (int, float)) or pd.api.types.is_number(value):

        try:
            return f"{float(value):,.2f}"
        except (ValueError, TypeError):
            return str(value)

    return str(value)


def format_results_dataframe(df):
    """
    Create a presentation-friendly copy of the result dataframe.
    """

    formatted_df = df.copy()

    for column in formatted_df.columns:

        if pd.api.types.is_numeric_dtype(formatted_df[column]):

            formatted_df[column] = formatted_df[column].apply(
                lambda value: format_number(value, column)
            )

    return formatted_df


# ============================================================
# KPI LOGIC
# ============================================================

def display_kpi(df):
    """
    Display one-row numeric results as separate KPI cards.

    Example:

        total_revenue
        total_orders
        total_customers
        cancelled_orders

    becomes four separate KPI cards.
    """

    # KPI cards require exactly one row
    if len(df) != 1:
        return False

    numeric_columns = []

    for column in df.columns:

        value = df.iloc[0][column]

        if pd.api.types.is_number(value) and not pd.isna(value):
            numeric_columns.append(column)

    # Nothing numeric to display
    if not numeric_columns:
        return False

    # Limit extreme layouts
    # More than 6 metrics will be split across rows.
    chunk_size = 6

    for start in range(0, len(numeric_columns), chunk_size):

        current_columns = numeric_columns[
            start:start + chunk_size
        ]

        kpi_columns = st.columns(len(current_columns))

        for i, column in enumerate(current_columns):

            value = df.iloc[0][column]

            label = pretty_name(column)

            formatted_value = format_number(
                value,
                column
            )

            with kpi_columns[i]:

                st.metric(
                    label=label,
                    value=formatted_value
                )

    return True


# ============================================================
# AUTOMATIC CHART LOGIC
# ============================================================

def create_automatic_chart(columns, rows):
    """
    Automatically select an appropriate chart
    based on returned database columns.
    """

    if not rows or not columns:
        return False

    df = pd.DataFrame(rows, columns=columns)

    if df.empty:
        return False

    # --------------------------------------------------------
    # Identify column types
    # --------------------------------------------------------

    date_columns = []
    numeric_columns = []
    categorical_columns = []

    for column in df.columns:

        series = df[column]

        # Numeric
        if pd.api.types.is_numeric_dtype(series):
            numeric_columns.append(column)
            continue

        # Try datetime detection
        converted_dates = pd.to_datetime(
            series,
            errors="coerce"
        )

        if (
            converted_dates.notna().sum() >=
            max(1, int(len(series) * 0.7))
        ):
            date_columns.append(column)
            continue

        # Category
        if series.nunique(dropna=True) <= 50:
            categorical_columns.append(column)

    # --------------------------------------------------------
    # MONTHLY / TIME-SERIES CHART
    # --------------------------------------------------------

    if date_columns and numeric_columns:

        date_column = date_columns[0]
        numeric_column = numeric_columns[0]

        chart_df = df.copy()

        chart_df[date_column] = pd.to_datetime(
            chart_df[date_column],
            errors="coerce"
        )

        chart_df = chart_df.dropna(
            subset=[date_column]
        )

        if chart_df.empty:
            return False

        # Detect monthly data and normalize to month
        chart_df[date_column] = (
            chart_df[date_column]
            .dt.to_period("M")
            .dt.to_timestamp()
        )

        # Aggregate duplicate months
        chart_df = (
            chart_df
            .groupby(date_column, as_index=False)[numeric_column]
            .sum()
            .sort_values(date_column)
        )

        if len(chart_df) >= 2:

            y_title = pretty_name(numeric_column)

            fig = px.line(
                chart_df,
                x=date_column,
                y=numeric_column,
                markers=True,
                title=f"{y_title} Over Time"
            )

            fig.update_layout(
                xaxis_title="Month",
                yaxis_title=y_title,
                hovermode="x unified"
            )

            fig.update_xaxes(
                tickformat="%b %Y",
                tickangle=-45
            )

            if is_currency_column(numeric_column):

                fig.update_yaxes(
                    tickprefix="R$ ",
                    separatethousands=True,
                    tickformat=",.2f"
                )

            elif is_count_column(numeric_column):

                fig.update_yaxes(
                    separatethousands=True,
                    tickformat=",d"
                )

            elif is_rate_column(numeric_column):

                fig.update_yaxes(
                    ticksuffix="%"
                )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            return True

    # --------------------------------------------------------
    # CATEGORY + NUMERIC → BAR CHART
    # --------------------------------------------------------

    if categorical_columns and numeric_columns:

        category_column = categorical_columns[0]
        numeric_column = numeric_columns[0]

        chart_df = df[
            [category_column, numeric_column]
        ].copy()

        chart_df[category_column] = (
            chart_df[category_column]
            .astype(str)
            .str.replace("_", " ", regex=False)
            .str.replace("-", " ", regex=False)
            .str.title()
        )

        chart_df = chart_df.sort_values(
            numeric_column,
            ascending=True
        )

        # Avoid unreadable charts
        if len(chart_df) > 30:
            chart_df = chart_df.tail(30)

        fig = px.bar(
            chart_df,
            x=numeric_column,
            y=category_column,
            orientation="h",
            title=f"{pretty_name(numeric_column)} by "
                  f"{pretty_name(category_column)}"
        )

        fig.update_layout(
            xaxis_title=pretty_name(numeric_column),
            yaxis_title=pretty_name(category_column)
        )

        if is_currency_column(numeric_column):

            fig.update_xaxes(
                tickprefix="R$ ",
                separatethousands=True,
                tickformat=",.2f"
            )

        elif is_count_column(numeric_column):

            fig.update_xaxes(
                separatethousands=True,
                tickformat=",d"
            )

        elif is_rate_column(numeric_column):

            fig.update_xaxes(
                ticksuffix="%"
            )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        return True

    # --------------------------------------------------------
    # TWO NUMERIC COLUMNS → SCATTER
    # --------------------------------------------------------

    if len(numeric_columns) >= 2:

        x_column = numeric_columns[0]
        y_column = numeric_columns[1]

        fig = px.scatter(
            df,
            x=x_column,
            y=y_column,
            title=f"{pretty_name(y_column)} vs "
                  f"{pretty_name(x_column)}"
        )

        fig.update_layout(
            xaxis_title=pretty_name(x_column),
            yaxis_title=pretty_name(y_column)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        return True

    return False


# ============================================================
# CSV DOWNLOAD
# ============================================================

def create_csv_download(df):
    """
    Convert dataframe into CSV bytes.
    """

    csv_buffer = io.StringIO()

    writer = csv.writer(csv_buffer)

    writer.writerow(df.columns)

    for row in df.itertuples(index=False):

        writer.writerow(row)

    return csv_buffer.getvalue().encode("utf-8")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("📚 Query History")

    if st.session_state.query_history:

        for i, item in enumerate(
            reversed(st.session_state.query_history),
            start=1
        ):

            st.caption(
                f"{i}. {item['question']}"
            )

    else:

        st.caption(
            "Your previous questions will appear here."
        )

    st.divider()

    if st.button(
        "🗑️ Clear History",
        use_container_width=True
    ):

        st.session_state.query_history = []

        st.rerun()

    st.divider()

    st.markdown("### Example Questions")

    st.markdown(
        """
        **Customers**
        - How many customers are there?
        - Who are the top 10 customers by spending?

        **Orders**
        - How many orders were cancelled?
        - How many orders were delivered?

        **Revenue**
        - What is the total revenue?
        - Show monthly revenue.

        **Products**
        - What are the top 10 products by revenue?
        - Which products have the highest sales?

        **Sellers**
        - Who are the top sellers by revenue?

        **Combined KPIs**
        - Show total revenue, total orders,
          total customers and cancelled orders.
        """
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🤖 AI Data Analyst Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    Ask questions about your e-commerce data using natural language.
    The agent converts your question into safe SQL, executes it in
    PostgreSQL, and presents the result using tables, KPIs and charts.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PIPELINE
# ============================================================

st.markdown(
    """
    <div class="pipeline">
    <b>Question</b>
    →
    <b>Gemini</b>
    →
    <b>SQL</b>
    →
    <b>Safety Validation</b>
    →
    <b>PostgreSQL</b>
    →
    <b>KPI / Visualization</b>
    →
    <b>AI Analysis</b>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# QUESTION INPUT
# ============================================================

question = st.text_input(
    "Ask your data question",
    placeholder=(
        "Example: What are the top 10 customers "
        "by total spending?"
    )
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze_button = st.button(
    "🔍 Analyze",
    type="primary",
    use_container_width=True
)


# ============================================================
# MAIN ANALYSIS
# ============================================================

if analyze_button:

    if not question.strip():

        st.warning(
            "Please enter a question first."
        )

        st.stop()

    # --------------------------------------------------------
    # Step 1 — Generate SQL
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">1️⃣ Generated SQL</div>',
        unsafe_allow_html=True
    )

    with st.spinner("Generating SQL..."):

        try:

            sql = generate_sql(question)

        except Exception as e:

            error_message = str(e)

            if "429" in error_message or "quota" in error_message.lower():

                st.error(
                    "Gemini API quota has been reached. "
                    "The SQL generation service cannot process "
                    "another request right now."
                )

                st.info(
                    "The PostgreSQL database, SQL validator and "
                    "Streamlit application are still working. "
                    "You can continue development without repeatedly "
                    "calling Gemini."
                )

            else:

                st.error(
                    f"Could not generate SQL: {error_message}"
                )

            st.stop()

    if not sql:

        st.error(
            "Gemini did not return a SQL query."
        )

        st.stop()

    st.code(
        sql,
        language="sql"
    )


    # --------------------------------------------------------
    # Step 2 — Validate SQL
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">2️⃣ SQL Safety Validation</div>',
        unsafe_allow_html=True
    )

    is_valid, validation_message = validate_sql(sql)

    if is_valid:

        st.success(
            f"✅ {validation_message}"
        )

    else:

        st.error(
            f"❌ {validation_message}"
        )

        st.stop()


    # --------------------------------------------------------
    # Step 3 — Execute PostgreSQL Query
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">3️⃣ Database Result</div>',
        unsafe_allow_html=True
    )

    with st.spinner("Executing query in PostgreSQL..."):

        try:

            columns, rows = execute_query(sql)

        except Exception as e:

            st.error(
                f"Database execution failed: {e}"
            )

            st.stop()

    if columns is None or rows is None:

        st.error(
            "The database could not execute the query."
        )

        st.stop()

    if len(rows) == 0:

        st.info(
            "The query executed successfully, "
            "but no matching records were found."
        )

        st.stop()


    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    df = pd.DataFrame(
        rows,
        columns=columns
    )


    # --------------------------------------------------------
    # Step 4 — KPIs
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">4️⃣ Key Metrics</div>',
        unsafe_allow_html=True
    )

    kpi_displayed = display_kpi(df)


    # --------------------------------------------------------
    # Step 5 — Automatic Visualization
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">5️⃣ Visualization</div>',
        unsafe_allow_html=True
    )

    chart_displayed = create_automatic_chart(
        columns,
        rows
    )


    if not chart_displayed:

        st.info(
            "No automatic chart was created for this result. "
            "The data is better represented as a table."
        )


    # --------------------------------------------------------
    # Step 6 — Result Table
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">6️⃣ Result Table</div>',
        unsafe_allow_html=True
    )

    formatted_df = format_results_dataframe(df)

    st.dataframe(
        formatted_df,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # CSV Download
    # --------------------------------------------------------

    csv_data = create_csv_download(df)

    st.download_button(
        label="⬇️ Download Results as CSV",
        data=csv_data,
        file_name="query_results.csv",
        mime="text/csv",
        use_container_width=True
    )


    # --------------------------------------------------------
    # Step 7 — AI Analysis
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">7️⃣ AI Analyst Explanation</div>',
        unsafe_allow_html=True
    )

    with st.spinner("Generating analyst explanation..."):

        try:

            answer = generate_answer(
                question,
                columns,
                rows
            )

            if answer:

                st.info(answer)

            else:

                st.info(
                    "The database returned the result successfully, "
                    "but an AI explanation was not generated."
                )

        except Exception as e:

            error_message = str(e)

            if (
                "429" in error_message
                or "quota" in error_message.lower()
            ):

                st.warning(
                    "AI explanation is temporarily unavailable "
                    "because the Gemini API quota has been reached."
                )

                st.caption(
                    "The SQL query and PostgreSQL result above "
                    "are still valid and available."
                )

            else:

                st.warning(
                    f"AI explanation unavailable: {error_message}"
                )


    # --------------------------------------------------------
    # Save Query History
    # --------------------------------------------------------

    st.session_state.query_history.append(
        {
            "question": question,
            "sql": sql
        }
    )


    # Keep history manageable
    if len(st.session_state.query_history) > 20:

        st.session_state.query_history = (
            st.session_state.query_history[-20:]
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Data Analyst Agent • Natural Language → SQL → "
    "PostgreSQL → Analytics"
)