from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import app.models
from app.api.posts.router import router as post_router
from app.api.auth.router import router as auth_router
from app.api.uploads.router import router as upload_router
from app.api.tags.router import router as tag_router
from app.api.categories.router import router as category_router
from app.core.db import Base, engine
from app.core.middleware import register_middleware
from app.services.file_storage import MEDIA_DIR, ensure_media_dir


def create_app() -> FastAPI:
    app = FastAPI(title="Mini Blog")
    Base.metadata.create_all(bind=engine)
    register_middleware(app)

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(post_router)
    app.include_router(upload_router)
    app.include_router(tag_router)
    app.include_router(category_router)

    ensure_media_dir()
    app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

    return app


app = create_app()
