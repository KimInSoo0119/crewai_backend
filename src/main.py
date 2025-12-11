import uvicorn
from fastapi import FastAPI
from src.controller import agent_controller, task_controller

app = FastAPI(title="Crewai Backend API")

app.include_router(
    agent_controller.router, 
    prefix="/api/v1/agents", 
    tags=["Agents"]
)

app.include_router(
    task_controller.router, 
    prefix="/api/v1/tasks", 
    tags=["Tasks"]
)
