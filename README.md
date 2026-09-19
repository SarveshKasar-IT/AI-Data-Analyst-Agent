# 🤖 AI Data Analyst Agent

> Ask questions about e-commerce data in natural language and get AI-generated insights from PostgreSQL.

## 🚀 Live Demo

[![Open Live Demo](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-data-analyst-agent-dxquvd474xzygrt4fusnwa.streamlit.app/)

**[👉 Open the Live Demo](https://ai-data-analyst-agent-dxquvd474xzygrt4fusnwa.streamlit.app/)**

# 🤖 AI Data Analyst Agent

An AI-powered data analytics application that allows users to ask questions about e-commerce data in natural language. The agent converts the question into SQL using Google Gemini, validates the generated SQL for safety, executes the approved query against PostgreSQL, and presents the result through KPI cards, tables, charts, and an optional AI-generated explanation.

## 📌 Project Overview

Traditional data analysis often requires users to know SQL before they can answer business questions.

This project provides a natural-language interface:

**User Question → Gemini → SQL → Safety Validation → PostgreSQL → KPI / Visualization → AI Explanation**

Example:

> "Show total revenue, total orders, total customers and cancelled orders."

The application can turn that request into a safe read-only SQL query, execute it against the analytics views, and display the returned metrics as separate KPI cards.

---

## ✨ Features

### Natural-language analytics
Ask questions without writing SQL manually.

Examples:
- How many orders were cancelled?
- What are the top 10 customers by total spending?
- Show monthly revenue.
- Which products have the highest revenue?
- Who are the top sellers by revenue?
- Show total revenue, total orders, total customers and cancelled orders.

### AI SQL generation
Google Gemini converts the user's natural-language question into PostgreSQL SQL.

### SQL safety validation
Generated SQL is checked before execution.

The validator:
- Allows only `SELECT` queries
- Blocks write/destructive commands
- Blocks multiple SQL statements
- Blocks SQL comments
- Blocks PostgreSQL system objects
- Allows only approved analytics views
- Blocks selected dangerous PostgreSQL functions

### PostgreSQL analytics
Queries run against curated analytics views instead of raw tables.

Approved views:

- `public.v_customer_analytics`
- `public.v_order_analytics`
- `public.v_product_analytics`
- `public.v_revenue_analytics`
- `public.v_seller_analytics`

### Automatic KPI cards
A one-row query containing multiple numeric metrics is automatically displayed as separate KPI cards.

Example metrics:
- Total Revenue
- Total Orders
- Total Customers
- Cancelled Orders

### Brazilian currency formatting
Revenue and monetary metrics use Brazilian formatting.

Example:

`R$ 13.450.000,75`

### Automatic visualizations
The app selects a chart based on the returned data:

- Date + numeric → line chart
- Category + numeric → horizontal bar chart
- Two numeric columns → scatter plot
- Single-row numeric result → KPI cards

### Clean result tables
Returned database results are displayed in a readable table.

### CSV export
Users can download query results as CSV.

### Query history
Recent questions are stored in the Streamlit session and displayed in the sidebar.

### Error handling
The application handles:
- Empty questions
- Invalid SQL
- Database errors
- Empty query results
- Gemini API quota errors
- AI explanation failures

---

# 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │       User          │
                         │ Natural Language    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     Streamlit       │
                         │       app.py        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Gemini / GenAI    │
                         │  SQL Generation     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   SQL Validator     │
                         │ sql_validator.py    │
                         └──────────┬──────────┘
                                    │
                             Safe SELECT only
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     PostgreSQL      │
                         │   Query Execution   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Analytics Result    │
                         │ KPI / Table / Chart │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Gemini Explanation  │
                         │  Business Summary   │
                         └─────────────────────┘
```

---

# 📁 Final Project Structure

```text
AI-Data-Analyst-Agent/
│
├── app.py
├── sql_generator.py
├── sql_validator.py
├── query_executor.py
├── answer_generator.py
├── db.py
│
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
│
├── sql/
│   └── analytics_views.sql
│
├── data/
│   └── README.md
│
└── assets/
    └── screenshots/
        └── dashboard.png
```

### Core files

| File | Purpose |
|---|---|
| `app.py` | Streamlit user interface and complete application workflow |
| `sql_generator.py` | Generates PostgreSQL SQL from natural-language questions |
| `sql_validator.py` | Validates generated SQL before database execution |
| `query_executor.py` | Connects to PostgreSQL and executes approved queries |
| `answer_generator.py` | Generates concise natural-language explanations |
| `db.py` | Database/schema inspection utility |
| `requirements.txt` | Python dependencies |
| `.env` | Local secrets and database configuration |
| `.env.example` | Safe template for environment variables |
| `sql/` | SQL definitions/documentation for analytics views |
| `assets/` | Screenshots and portfolio assets |

> Never commit `.env` or any file containing API keys/passwords.

---

# 🛠️ Technology Stack

- **Python**
- **Streamlit**
- **Google Gemini / `google-genai`**
- **PostgreSQL**
- **psycopg2**
- **Pandas**
- **Plotly**
- **python-dotenv**

---

# ⚙️ Requirements

Before running the project, install:

- Python 3.10+
- PostgreSQL
- A Gemini API key
- Git (optional, for version control)

Check Python:

```powershell
python --version
```

Check PostgreSQL:

```powershell
psql --version
```

---

# 🚀 Setup Instructions

## 1. Clone the project

If using Git:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd AI-Data-Analyst-Agent
```

Or open the existing project directory directly.

---

## 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

You should see:

```text
(.venv)
```

at the beginning of your terminal prompt.

---

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a file named:

```text
.env
```

in the project root.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key

DB_HOST=localhost
DB_NAME=your_database_name
DB_USER=postgres
DB_PASSWORD=your_postgresql_password
DB_PORT=5432
```

### Variable descriptions

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `DB_HOST` | PostgreSQL host |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_PORT` | PostgreSQL port, normally `5432` |

### Security

Do **not** write secrets directly into Python files.

Do **not** commit `.env` to GitHub.

The `.gitignore` should contain:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

---

# 🗄️ PostgreSQL Setup

The application expects the following analytics views:

```text
public.v_customer_analytics
public.v_order_analytics
public.v_product_analytics
public.v_revenue_analytics
public.v_seller_analytics
```

The views provide a controlled analytics layer between the application and the underlying database.

### Customer analytics

```text
public.v_customer_analytics
```

Typical fields include:

```text
customer_id
total_orders
unique_products
total_product_value
total_freight_value
total_spend
average_item_value
first_purchase_date
last_purchase_date
delivered_orders
cancelled_orders
late_delivery_rate
```

### Order analytics

```text
public.v_order_analytics
```

Includes order, customer, product, seller, price and delivery information.

### Product analytics

```text
public.v_product_analytics
```

Includes product sales, sellers, prices and revenue metrics.

### Revenue analytics

```text
public.v_revenue_analytics
```

Includes monthly revenue, orders, customers and delivery metrics.

### Seller analytics

```text
public.v_seller_analytics
```

Includes seller orders, products, revenue and pricing metrics.

---

# 🔎 Inspect the Database

Run:

```powershell
python db.py
```

This utility can be used to inspect the analytics view schemas and confirm that the expected database objects are available.

---

# ▶️ Run the Application

Make sure the virtual environment is active:

```powershell
.\.venv\Scripts\Activate.ps1
```

Then start Streamlit:

```powershell
streamlit run app.py
```

Streamlit will provide a local browser address, normally similar to:

```text
http://localhost:8501
```

Open that address in your browser.

---

# 💬 Example Questions

## Customer analysis

```text
How many customers are there?
```

```text
What are the top 10 customers by total spending?
```

```text
Show customers with the highest number of orders.
```

## Order analysis

```text
How many orders were cancelled?
```

```text
How many orders were delivered?
```

```text
Show the top 10 orders by price.
```

## Revenue analysis

```text
What is the total revenue?
```

```text
Show monthly revenue.
```

```text
Show total revenue, total orders, total customers and cancelled orders.
```

## Product analysis

```text
What are the top 10 products by revenue?
```

```text
Which products have the highest number of units sold?
```

## Seller analysis

```text
Who are the top sellers by revenue?
```

```text
Which sellers have the most orders?
```

---

# 📊 Example KPI Result

A combined KPI query can return:

```text
total_revenue     total_orders     total_customers     cancelled_orders
---------------   -------------    ----------------    ----------------
13,450,000.75     99,441           96,096              625
```

The application presents these as separate KPI cards:

```text
┌────────────────────┐
│ Total Revenue      │
│ R$ 13.450.000,75   │
└────────────────────┘

┌────────────────────┐
│ Total Orders       │
│ 99,441             │
└────────────────────┘

┌────────────────────┐
│ Total Customers    │
│ 96,096             │
└────────────────────┘

┌────────────────────┐
│ Cancelled Orders   │
│ 625                │
└────────────────────┘
```

---

# 🔒 SQL Safety

The generated SQL is never sent directly to PostgreSQL without validation.

The flow is:

```text
Natural Language
       ↓
Gemini SQL Generation
       ↓
SQL Validator
       ↓
Approved?
   ↙       ↘
 NO         YES
 ↓           ↓
STOP     PostgreSQL
```

The validator blocks commands such as:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
CREATE
GRANT
REVOKE
COPY
VACUUM
CALL
DO
EXECUTE
MERGE
COMMENT
REFRESH
```

It also restricts database access to the approved analytics views.

---

# 🧪 Testing

Test the SQL generator:

```powershell
python sql_generator.py
```

Example:

```text
Enter your question:
What are the top 10 customers by total spending?
```

The application should produce SQL similar to:

```sql
SELECT
    customer_id,
    total_spend
FROM public.v_customer_analytics
ORDER BY total_spend DESC NULLS LAST
LIMIT 10;
```

Test the Streamlit application:

```powershell
streamlit run app.py
```

Recommended tests:

1. Single KPI query
2. Multiple KPI query
3. Top-N query
4. Monthly revenue query
5. Category/revenue query
6. Invalid or unsupported SQL behavior
7. Empty-result query
8. CSV download

---

# 🧯 Troubleshooting

## 1. `ModuleNotFoundError`

Example:

```text
ModuleNotFoundError: No module named 'streamlit'
```

Activate the virtual environment and reinstall:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 2. Gemini API error

Check:

```env
GEMINI_API_KEY=...
```

Make sure the key is valid and the `.env` file is in the project root.

Restart Streamlit after changing environment variables.

---

## 3. Gemini `429` / quota error

You may see an error indicating that the Gemini request quota has been exhausted.

This means the application reached the available API request limit.

The database and SQL validation components can still be tested independently.

Avoid repeatedly pressing **Analyze**, because each full request can consume additional API quota.

---

## 4. PostgreSQL connection error

Check:

```env
DB_HOST=localhost
DB_NAME=your_database_name
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

Then verify PostgreSQL is running.

You can also test:

```powershell
psql -U postgres
```

---

## 5. `relation does not exist`

Example:

```text
relation "public.v_customer_analytics" does not exist
```

The required analytics view has not been created in the selected database, or the application is connected to the wrong database.

Run:

```powershell
python db.py
```

and confirm that the expected views are listed.

---

## 6. SQL validation fails

The validator intentionally rejects SQL that:

- Is not a `SELECT`
- Uses unauthorized tables/views
- Contains multiple statements
- Contains comments
- Uses blocked commands
- References PostgreSQL system objects
- Uses selected dangerous functions

This is a security feature rather than an application failure.

---

## 7. No chart appears

Not every result is suitable for visualization.

The application automatically creates charts when it detects useful combinations such as:

```text
Date + Numeric
Category + Numeric
Numeric + Numeric
```

Otherwise, the result is shown as a table.

---

## 8. No rows returned

The SQL may have executed successfully but found no matching records.

The application reports this instead of treating it as a database failure.

---

# 🧩 Important Design Decisions

### Why use analytics views?

Instead of allowing Gemini to query arbitrary raw tables, the application exposes a controlled set of business-oriented views.

This makes SQL generation simpler and reduces the database surface available to generated queries.

### Why validate SQL?

AI-generated SQL should not be trusted blindly.

The validation layer provides an additional safety boundary before execution.

### Why separate SQL generation and execution?

This separation makes the architecture easier to test:

```text
sql_generator.py
        ↓
sql_validator.py
        ↓
query_executor.py
```

Each component has a clear responsibility.

### Why use automatic visualization?

Users asking natural-language questions should not need to manually choose a chart type for every query.

The application uses the structure of the returned data to select a reasonable visualization.

---

# 🎯 Project Objective

The goal of this project is to demonstrate how modern AI can be combined with traditional data engineering and analytics technologies to create a natural-language data analysis workflow.

The project combines:

- Generative AI
- Natural-language interfaces
- SQL generation
- SQL security validation
- PostgreSQL
- Data analytics
- Automated visualization
- Business-oriented result interpretation

---

# 💼 Project Description

**AI Data Analyst Agent | Python, Gemini, PostgreSQL, Streamlit, SQL, Plotly**

- Built an AI-powered natural-language data analyst that converts business questions into PostgreSQL queries using Google Gemini and presents results through automated KPIs, tables, and visualizations.
- Implemented a SQL safety-validation layer that restricts generated queries to read-only `SELECT` operations and approved analytics views before database execution.
- Developed an interactive Streamlit dashboard with automatic chart selection, Brazilian currency formatting, CSV export, query history, and AI-generated business explanations.

---

# 🎤 Platform Explanation

A simple way to explain the project:

> "I built an AI Data Analyst Agent that allows users to ask questions about e-commerce data in natural language. Gemini converts the question into SQL, but I don't execute the generated SQL directly. I first pass it through a validation layer that allows only safe SELECT queries against approved analytics views. The validated query is executed in PostgreSQL, and the result is presented in Streamlit using KPI cards, tables, and automatic charts. Gemini can then provide a simple business explanation of the result."

---

# 🚀 Future Improvements

Possible future enhancements include:

- Authentication and user management
- Role-based database access
- Query result caching
- Persistent query history
- More advanced chart recommendations
- SQL parsing using a dedicated SQL parser
- Query performance monitoring
- Deployment to a cloud platform
- Database-level read-only user permissions
- Automated data-quality monitoring

---

# 📌 Project Status

The project is designed as a portfolio-ready demonstration of an end-to-end AI analytics workflow:

```text
Natural Language
       ↓
Generative AI
       ↓
SQL Generation
       ↓
SQL Security
       ↓
PostgreSQL
       ↓
Analytics
       ↓
Visualization
       ↓
Business Explanation
```

---

## License

This project is intended for educational, portfolio, and demonstration purposes.
