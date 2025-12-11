from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.service.agent import agent_service

router = APIRouter()

class AgentSave(BaseModel):
    id: Optional[int] = None 
    project_id: int
    role: str
    goal: str
    backstory: str
    model_id: int

@router.post("/save")
def save_agent(agent: AgentSave):
    try:
        response = agent_service.save_agent(agent)
        return response
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))