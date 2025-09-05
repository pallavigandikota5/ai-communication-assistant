from fastapi import APIRouter, UploadFile, File
import os, shutil

router = APIRouter()

@router.post("/upload")
async def upload_kb(file: UploadFile = File(...)):
    os.makedirs("kb", exist_ok=True)
    dest = os.path.join("kb", file.filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"ok": True, "file": file.filename}
