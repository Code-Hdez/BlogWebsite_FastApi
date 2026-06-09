from fastapi import APIRouter, File, UploadFile
from app.services.file_storage import save_upload_file

router = APIRouter(prefix="/upload", tags=["uploads"])


@router.post("/save")
async def save_file(file: UploadFile = File(...)):

    saved = save_upload_file(file)

    return {
        "filename": saved["filename"],
        "content_type": saved["content_type"],
        "url": saved["url"],
        "size": saved["size"],
        "chunk_size_used": saved["chunk_size_used"],
        "chunk_calls": saved["chunk_calls"],
        "chunk_size_sample": saved["chunk_size_sample"],
    }
