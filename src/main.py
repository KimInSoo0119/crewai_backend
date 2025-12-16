from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.controller import crew_controller, agent_controller, task_controller, llm_controller
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
    crew_controller.router, 
    prefix="/api/v1/crew", 
    tags=["Crew"]
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

app.include_router(
    llm_controller.router, 
    prefix="/api/v1/llm", 
    tags=["LLM"]
)