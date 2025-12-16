import requests
from src.repository.llm import llm_repo

def connection_llm(llmInfo):
    try:
        headers = {"Authorization": f"Bearer {llmInfo.api_key}"}
        api_url = f"{llmInfo.api_base}/models" 
        res = requests.get(api_url, headers=headers, timeout=5)
        if res.status_code != 200:
            raise RuntimeError(f"Failed to connect to LLM API. Status code: {res.status_code}")
        
        model_id = llm_repo.connection_llm(llmInfo)
        return {"success": True, "model_id": model_id, "message": "LLM connected and saved successfully"}
    except Exception as e:
        raise RuntimeError(f"error: {str(e)}")
    
def get_llm_list():
    try:
        response = llm_repo.get_llm_list()
        return response
    except Exception as e:
        raise RuntimeError(f"error: {str(e)}")
    
def get_provider_list():
    try:
        response = llm_repo.get_provider_list()
        return response
    except Exception as e:
        raise RuntimeError(f"error: {str(e)}")