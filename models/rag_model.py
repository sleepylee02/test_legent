def search_similar_cases(accident_description: str) -> list:
    """
    Mock function to simulate RAG system.
    This will be replaced with actual RAG implementation later.
    """
    return [
        {
            "case_id": "ACC001",
            "description": "Similar accident involving red sedan running red light",
            "resolution": "Driver of red sedan found at fault, insurance covered damages",
            "similarity_score": 0.85
        },
        {
            "case_id": "ACC002",
            "description": "Intersection collision with similar damage pattern",
            "resolution": "Both parties shared fault, split insurance coverage",
            "similarity_score": 0.72
        }
    ] 