import os
import tempfile
from typing import BinaryIO

def save_uploaded_video(uploaded_file: BinaryIO) -> str:
    """
    Save uploaded video to a temporary file and return the path.
    
    Args:
        uploaded_file: The uploaded file object from Streamlit
        
    Returns:
        str: Path to the temporary file
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name

def cleanup_temp_file(file_path: str) -> None:
    """
    Clean up temporary file after processing.
    
    Args:
        file_path: Path to the temporary file
    """
    if os.path.exists(file_path):
        os.unlink(file_path) 