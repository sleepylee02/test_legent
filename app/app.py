import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from models.vision_model import analyze_video
from models.rag_model import search_similar_cases
from models.llm_model import generate_analysis
from utils.file_handler import save_uploaded_video, cleanup_temp_file

# Set page config
st.set_page_config(page_title="사고 판단 챗봇", page_icon="⚖️")
st.title("⚖️ 한문철 스타일 사고 판단 챗봇 (기본 버전)")

# File uploader for video
uploaded_video = st.file_uploader("Upload accident video", type=['mp4', 'mov', 'avi'])

# Text input for additional information
text_input = st.text_area("Additional Information", 
                         placeholder="Enter any additional details about the accident...")

if uploaded_video is not None and st.button("Analyze Accident"):
    # Save uploaded video to temporary file
    video_path = save_uploaded_video(uploaded_video)

    try:
        # Show processing message
        with st.spinner('Processing video and analyzing accident...'):
            # Process video with vision model
            vision_result = analyze_video(video_path, text_input)
            
            # Display accident description
            st.subheader("Accident Description")
            st.write(vision_result["accident_description"])
            
            # Search for similar cases
            similar_cases = search_similar_cases(vision_result["accident_description"])
            
            # Display similar cases
            st.subheader("Similar Cases Found")
            for case in similar_cases:
                with st.expander(f"Case {case['case_id']} (Similarity: {case['similarity_score']:.2f})"):
                    st.write(f"Description: {case['description']}")
                    st.write(f"Resolution: {case['resolution']}")
            
            # Generate analysis
            analysis_result = generate_analysis(vision_result["accident_description"], similar_cases)
            
            # Display analysis
            st.subheader("Accident Analysis")
            st.write(analysis_result["raw_response"])
    
    finally:
        # Clean up temporary file
        cleanup_temp_file(video_path)

# Add some styling
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)