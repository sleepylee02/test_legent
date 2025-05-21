# config.py
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수 읽기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")