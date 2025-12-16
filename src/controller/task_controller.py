from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.service.task import task_service

router = APIRouter()

class TaskSave(BaseModel):
    id: Optional[int] = None
    project_id: int
    agent_id: int
    name: str
    description: str
    expected_output: str

@router.post("/save")
def save_task(task: TaskSave):
    try:
        response = task_service.save_task(task)
        return response
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/projects/{project_id}/tasks/{task_id}")
def get_task(project_id: int, task_id: int):
    try:
        response = task_service.get_task(project_id, task_id)
        if not response:
            raise HTTPException(404, "Task not found")
        return response
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))