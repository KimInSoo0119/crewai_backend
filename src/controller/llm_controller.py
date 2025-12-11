from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.service.llm import llm_service

router = APIRouter()

class llmInfo(BaseModel):
    api_key: str
    api_base: str

@router.post("/connection")
def connection_llm(llmInfo: llmInfo):
    try:
        response = llm_service.connection_llm(llmInfo)
        return response
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))