from fastapi import APIRouter, HTTPException
from src.service.crew import crew_service

router = APIRouter()
    
@router.get("/list")
def get_crew_list():
    try:
        response = crew_service.get_crew_list()
        return {"data": [response]}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))