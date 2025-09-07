from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.base import init_engine_and_session, create_all_tables_and_indexes
from app.api.routes import api_router

setup_logging()
engine, SessionLocal = init_engine_and_session()

app = FastAPI(title=settings.API_TITLE, version=settings.API_VERSION)
app.include_router(api_router, prefix="/v1")


@app.on_event("startup")
def on_startup() -> None:
    create_all_tables_and_indexes(engine)


@app.get("/v1/health")
def health():
    return {"status": "ok", "env": settings.APP_ENV, "db": "postgres+pgvector"}
