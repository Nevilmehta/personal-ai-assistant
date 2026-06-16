from fastapi import FastAPI

from app.api.routes.article_routes import router as article_router
from app.api.routes.dashboard_routes import router as dashboard_router
from app.api.routes.health_routes import router as health_router
from app.api.routes.ingestion_routes import router as ingestion_router
from app.api.routes.jarvis_routes import router as jarvis_router
from app.api.routes.rag_routes import router as rag_router
from app.api.routes.topic_routes import router as topic_router
from app.db.database import Base, engine


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Jarvis AI System",
    description="Personal AI Intelligence System",
    version="0.2.9",
)


@app.get("/")
def root():
    return {
        "message": "Jarvis AI System is running.",
        "phase": "Phase 2.9 - API Route Organization",
    }


app.include_router(health_router)
app.include_router(jarvis_router)
app.include_router(rag_router)
app.include_router(article_router)
app.include_router(topic_router)
app.include_router(ingestion_router)
app.include_router(dashboard_router)