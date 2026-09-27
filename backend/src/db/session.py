import ssl
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import settings


def _connect_args() -> dict:
    if settings.database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    if settings.database_url.startswith("postgresql") and settings.database_require_ssl:
        # RDSはNAT不要の構成上publicアクセスにしているため、SSL接続を必須にして通信を保護する
        return {"ssl_context": ssl.create_default_context()}
    return {}


engine = create_engine(settings.database_url, connect_args=_connect_args())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
