from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.controller import agent_controller, task_controller
from src.core.config import settings

app = FastAPI(title="Crewai Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
