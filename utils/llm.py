from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def ask_gpt(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "당신은 사고 판단을 도와주는 법률 상담 AI입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content