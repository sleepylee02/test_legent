from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_analysis(accident_description: str, similar_cases: list) -> dict:
    prompt = (
        f"Accident Description:\n{accident_description}\n\n"
        f"Similar Cases:\n" + "\n".join(f"- {case}" for case in similar_cases) + "\n\n"
        "Based on the above, provide:\n"
        "1. A detailed accident analysis\n"
        "2. Recommendations for the user\n"
        "3. An estimated liability statement"
    )

    chat_completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a car accident analysis expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )

    reply = chat_completion.choices[0].message.content

    return {
        "raw_response": reply
    }