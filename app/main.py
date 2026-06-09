from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api import commits, crashes, dashboard, projects, sessions, websocket, workers

app = FastAPI(title="Fuzz Flow Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix="/api")
app.include_router(commits.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(crashes.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(workers.router, prefix="/api")
app.include_router(websocket.router)


@app.get("/")
def root():
    return {"message": "Fuzz Flow Backend API"}
