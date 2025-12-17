from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.service.crew import crew_service

router = APIRouter()

class CrewData(BaseModel):
    title: str

class NodeData(BaseModel):
    id: str
    dbId: Optional[int]
    type: str
    position: dict
    data: dict

class EdgeData(BaseModel):
    id: str
    dbId: Optional[int]
    source: str
    target: str

class ExecuteFlowRequest(BaseModel):
    project_id: int
    nodes: List[NodeData]
    edges: List[EdgeData]

@router.post("/create")
def create_crew(crewData: CrewData):
    try:
        project_id = crew_service.create_crew(crewData)
        return {"data": project_id}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/list")
def get_crew_list():
    try:
        response = crew_service.get_crew_list()
        return {"data": response}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/flow/{project_id}")
def get_crew_flow(project_id: int):
    try:
        response = crew_service.get_crew_flow(project_id)
        return {"data": response}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/flow/execute")
def crew_flow_execute(request: ExecuteFlowRequest):
    try:
        crew_service.execute_flow(request.project_id, request.nodes, request.edges)
        return {"status": "success"}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))