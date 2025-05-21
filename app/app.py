import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from utils.llm import ask_gpt

st.set_page_config(page_title="사고 판단 챗봇", page_icon="⚖️")
st.title("⚖️ 한문철 스타일 사고 판단 챗봇 (기본 버전)")

user_input = st.text_area("🚗 사고 상황을 입력해주세요:")

if st.button("판단 요청") and user_input.strip():
    with st.spinner("판단 중입니다..."):
        response = ask_gpt(user_input.strip())
        st.success("🧠 GPT의 사고 판단")
        st.markdown(response)