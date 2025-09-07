from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.engine import Engine
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


def init_engine_and_session():
    engine = create_engine(settings.DB_DSN, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return engine, SessionLocal


engine, SessionLocal = init_engine_and_session()


def create_all_tables_and_indexes(engine: Engine) -> None:
    # Ensure extension
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    # Import models to register metadata
    from app.db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    # Create ANN index for embeddings (IVFFLAT with cosine)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS ix_chunk_embeddings_embedding
                ON chunk_embeddings
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
                """
            )
        )
    logger.info("DB schema ensured (tables + indexes).")
