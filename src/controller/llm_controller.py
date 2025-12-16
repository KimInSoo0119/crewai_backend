from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.service.llm import llm_service

router = APIRouter()

class llmInfo(BaseModel):
    name: str
    provider: str
    api_key: str
    api_base: str

@router.post("/connection")
def connection_llm(llmInfo: llmInfo):
    try:
        response = llm_service.connection_llm(llmInfo)
        return response
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/list")
def get_llm_list():
    try:
        response = llm_service.get_llm_list()
        return {"data": [response]}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/provider/list")
def get_provider_list():
    try:
        response = llm_service.get_provider_list()
        return {"data": [response]}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
