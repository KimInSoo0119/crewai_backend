from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Crewai Backend")

@app.get("/")
def read_root():
    return {"message": "Hello, Crewai!"}
