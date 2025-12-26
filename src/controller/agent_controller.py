from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.service.agent import agent_service
from typing import Optional, Any, Dict

router = APIRouter()

class AgentSave(BaseModel):
    id: Optional[int] = None 
    project_id: int
    role: str
    goal: str
    backstory: str
    model_id: Optional[int] = None

class ToolModel(BaseModel):
    name: str
    config: Optional[Dict[str, Any]] = {}

class AgentToolSaveRequest(BaseModel):
    agent_id: int
    tool: ToolModel

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
        return {"data": response}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/tools/save")
def save_agent_tools(tools: AgentToolSaveRequest):
    try:
        response = agent_service.save_agent_tools(tools)
        return {"data": response}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))