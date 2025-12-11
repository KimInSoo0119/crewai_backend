from src.repository.llm import llm_repo

def connection_llm(llmInfo):
    try:
        "llm connection 로직 구현"
        return {}
    except Exception as e:
        raise RuntimeError(f"error: {str(e)}")