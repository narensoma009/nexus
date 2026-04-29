from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import (
    hierarchy,
    programs,
    resources,
    ai_adoption,
    slides,
    chat,
    reports,
)

app = FastAPI(title="AT&T Account Platform API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(hierarchy.router, prefix="/api/hierarchy", tags=["hierarchy"])
app.include_router(programs.router, prefix="/api", tags=["programs"])
app.include_router(resources.router, prefix="/api/resources", tags=["resources"])
app.include_router(ai_adoption.router, prefix="/api/ai-adoption", tags=["ai-adoption"])
app.include_router(slides.router, prefix="/api/slides", tags=["slides"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.ENVIRONMENT}
