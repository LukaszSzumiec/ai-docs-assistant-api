from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.core.config import settings


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_api_key(x_api_key: str = Header(None)):
    if not settings.API_KEY:
        # auth disabled in dev if no API_KEY
        return
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="invalid API key")
