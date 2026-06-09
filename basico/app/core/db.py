import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_URL = f"sqlite:///{BASE_DIR / 'blog.db'}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

if not DATABASE_URL.startswith("sqlite"):
    raise RuntimeError("Este backend esta configurado para usar SQLite solamente.")

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=False, future=True, **engine_kwargs)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, class_=Session)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
