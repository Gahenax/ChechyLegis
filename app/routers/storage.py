from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File as FastAPIFile
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from pathlib import Path

from ..storage_service import StorageService
from .. import storage_utils, schemas
from ..database import get_db
from ..core.config import settings
from ..core.security import get_current_user, role_required

router = APIRouter(
    prefix="/api/files",
    tags=["Gestión de Archivos"]
)

def get_storage(db: Session = Depends(get_db)):
    return StorageService(db, settings.FILES_ROOT)

@router.post("/folders")
def create_folder(
    folder: schemas.FolderCreate,
    user: dict = Depends(role_required(["admin", "operator"])),
    storage: StorageService = Depends(get_storage)
):
    storage_utils.ensure_user_layout(settings.FILES_ROOT, user["id"])
    success = storage.create_folder(user["id"], folder.path)
    if not success:
        return JSONResponse(status_code=400, content={"error": {"code": "PATH_INVALID", "message": "Ruta inválida o fuera de sandbox"}})
    return {"status": "success", "path": folder.path}

@router.get("/folders")
def list_files(
    path: str = Query("", description="Ruta relativa para listar"),
    user: dict = Depends(get_current_user),
    storage: StorageService = Depends(get_storage)
):
    records = storage.list_files(user["id"], path)
    return records

@router.post("/upload")
async def upload_file(
    path: str = Query(...), 
    file: UploadFile = FastAPIFile(...),
    user: dict = Depends(role_required(["admin", "operator"])),
    storage: StorageService = Depends(get_storage)
):
    content = await file.read()
    record = storage.upload_file(user["id"], path, file.filename, content, file.content_type)
    if not record:
        return JSONResponse(status_code=400, content={"error": {"code": "UPLOAD_FAILED", "message": "Error al guardar el archivo"}})
    return record

@router.get("/download/{file_id}")
def download_file(
    file_id: str,
    user: dict = Depends(get_current_user),
    storage: StorageService = Depends(get_storage)
):
    path = storage.get_file_path(user["id"], file_id)
    if not path or not path.exists():
        return JSONResponse(status_code=404, content={"error": {"code": "FILE_NOT_FOUND", "message": "Archivo no existe"}})
    return FileResponse(path)

@router.post("/trash")
def trash_file(
    request: dict,
    user: dict = Depends(role_required(["admin", "operator"])),
    storage: StorageService = Depends(get_storage)
):
    file_id = request.get("file_id")
    success = storage.move_to_trash(user["id"], file_id)
    if not success:
        return JSONResponse(status_code=400, content={"error": {"code": "TRASH_FAILED", "message": "No se pudo mover a la papelera"}})
    return {"status": "success"}
