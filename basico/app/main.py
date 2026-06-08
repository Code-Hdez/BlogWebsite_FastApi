import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from app.core.db import Base, engine
from app.api.posts.router import router as post_router
from app.api.auth.router import router as auth_router
from app.api.uploads.router import router as upload_router
from app.api.tags.router import router as tag_router

load_dotenv()

MEDIA_DIR = "app/media"


def create_app() -> FastAPI:
    app = FastAPI(title="Mini Blog")
    Base.metadata.create_all(bind=engine)  # dev
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(post_router)
    app.include_router(upload_router)
    app.include_router(tag_router)

    os.makedirs(MEDIA_DIR, exist_ok=True)
    app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

    return app


app = create_app()
