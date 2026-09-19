import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-3.6-flash"


def generate_answer(question, columns, rows):

    # Convert database results into readable text
    result_text = ""

    for row in rows:
        result_text += " | ".join(str(value) for value in row)
        result_text += "\n"

    prompt = f"""
You are an AI Data Analyst.

The user asked:

{question}

The PostgreSQL database returned these columns:

{columns}

The database returned these results:

{result_text}

Explain the result to the user in simple, professional language.

Rules:
1. Answer the user's question directly.
2. Use ONLY the provided database results.
3. Do not invent information.
4. Mention important numbers from the result.
5. If the result contains multiple rows, summarize the key pattern.
6. Keep the explanation concise.
7. Do not mention SQL, Gemini, APIs, or internal implementation.
"""

    response = client.interactions.create(
        model=MODEL_NAME,
        input=prompt
    )

    return response.output_text.strip()