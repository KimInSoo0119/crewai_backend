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