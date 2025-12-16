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
    
@router.get("/projects/{project_id}/agents/{agent_id}")
def get_agent(project_id: int, agent_id: int):
    try:
        response = agent_service.get_agent(project_id, agent_id)
        if not response:
            raise HTTPException(404, "Agent not found")
        return response
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))