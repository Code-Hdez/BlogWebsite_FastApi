import os
import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException, status

MEDIA_DIR = Path(__file__).resolve().parents[1] / "media"
ALLOW_MIME = ["image/png", "image/jpeg"]
MAX_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
CHUNK_SIZE = 1024 * 1024


def ensure_media_dir() -> None:
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)


def save_upload_file(file: UploadFile) -> dict:
    if file.content_type not in ALLOW_MIME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten imagenes PNG o JPEG",
        )

    ensure_media_dir()
    ext = Path(file.filename or "").suffix
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = MEDIA_DIR / filename

    class _ChunkCounter:
        def __init__(self, f):
            self._f = f
            self.calls = 0
            self.sizes = []

        def read(self, n=-1):
            data = self._f.read(n)
            if data:
                self.calls += 1
                self.sizes.append(len(data))
            return data

        def __getattr__(self, name):  # delega cualquier otro atributo
            return getattr(self._f, name)

    reader = _ChunkCounter(file.file)

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(reader, buffer, length=CHUNK_SIZE)

    size = file_path.stat().st_size
    if size > MAX_MB * CHUNK_SIZE:
        file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Archivo demasiado grande(>{MAX_MB} MB)",
        )

    return {
        "filename": filename,
        "content_type": file.content_type,
        "url": f"/media/{filename}",
        "size": size,
        "chunk_size_used": CHUNK_SIZE,
        "chunk_calls": reader.calls,
        "chunk_size_sample": reader.sizes[:5],
    }
