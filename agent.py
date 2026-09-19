from sql_generator import generate_sql
from query_executor import execute_query
from sql_validator import validate_sql
from answer_generator import generate_answer


def run_agent(user_question):

    print("\n" + "=" * 60)
    print("AI DATA ANALYST AGENT")
    print("=" * 60)

    print("\nQuestion:")
    print(user_question)

    # ---------------------------------------------------------
    # STEP 1 — Generate SQL
    # ---------------------------------------------------------

    print("\nGenerating SQL...")

    try:

        sql = generate_sql(user_question)

    except Exception as e:

        error_message = str(e)

        if "429" in error_message or "quota" in error_message.lower():

            print("\nGemini API quota is currently unavailable.")
            print("SQL generation cannot be performed right now.")

        else:

            print("\nGemini API error:")
            print(error_message)

        return

    print("\nGenerated SQL:")
    print(sql)

    # ---------------------------------------------------------
    # STEP 2 — Validate SQL
    # ---------------------------------------------------------

    print("\nValidating SQL...")

    is_valid, validation_message = validate_sql(sql)

    if not is_valid:

        print("\nSQL BLOCKED!")
        print(f"Reason: {validation_message}")

        return

    print("SQL validation passed.")

    # ---------------------------------------------------------
    # STEP 3 — Execute SQL
    # ---------------------------------------------------------

    print("\nExecuting SQL...")

    columns, rows = execute_query(sql)

    if columns is None:

        print("\nCould not execute the generated SQL.")

        return

    # ---------------------------------------------------------
    # STEP 4 — Display results
    # ---------------------------------------------------------

    print("\nResults:")
    print("-" * 60)

    if not rows:

        print("No results found.")

        return

    print(" | ".join(columns))

    print("-" * 60)

    for row in rows:

        print(" | ".join(str(value) for value in row))

    print("-" * 60)

    print(f"\nRows returned: {len(rows)}")

    # ---------------------------------------------------------
    # STEP 5 — Generate natural-language explanation
    # ---------------------------------------------------------

    print("\nAI Analysis:")

    try:

        answer = generate_answer(
            user_question,
            columns,
            rows
        )

        print("-" * 60)
        print(answer)
        print("-" * 60)

    except Exception as e:

        error_message = str(e)

        if "429" in error_message or "quota" in error_message.lower():

            print("AI explanation is temporarily unavailable because")
            print("the Gemini API quota has been reached.")

        else:

            print("Could not generate AI explanation.")
            print(f"Reason: {error_message}")


if __name__ == "__main__":

    print("\nAI Data Analyst Agent")
    print("Type 'exit' to quit.")

    while True:

        question = input("\nAsk a data question: ")

        if question.lower().strip() == "exit":

            print("\nGoodbye!")

            break

        if not question.strip():

            print("Please enter a question.")

            continue

        run_agent(question)