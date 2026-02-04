import os
import shutil
import hashlib
import uuid
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from . import models, schemas, storage_utils

class StorageService:
    def __init__(self, db: Session, base_root: str):
        self.db = db
        self.base_root = base_root

    def _get_user_db_record(self, user_id: str, file_id: str) -> Optional[models.FileRecord]:
        return self.db.query(models.FileRecord).filter(
            models.FileRecord.user_id == user_id,
            models.FileRecord.file_id == file_id
        ).first()

    def create_folder(self, user_id: str, path: str) -> bool:
        target = storage_utils.sanitize_path(self.base_root, user_id, path)
        if not target:
            return False
        target.mkdir(parents=True, exist_ok=True)
        return True

    def upload_file(self, user_id: str, relative_path: str, file_name: str, content: bytes, mime_type: str) -> Optional[models.FileRecord]:
        target_dir = storage_utils.sanitize_path(self.base_root, user_id, relative_path)
        if not target_dir:
            return None
        
        target_dir.mkdir(parents=True, exist_ok=True)
        file_path = target_dir / file_name
        
        # Guardar archivo físicamente
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Calcular SHA256
        sha256 = hashlib.sha256(content).hexdigest()
        file_id = str(uuid.uuid4())
        
        # Persistir en DB
        db_record = models.FileRecord(
            file_id=file_id,
            user_id=user_id,
            name=file_name,
            path=str(Path(relative_path) / file_name),
            mime_type=mime_type,
            size_bytes=len(content),
            sha256=sha256
        )
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def list_files(self, user_id: str, relative_path: str) -> List[models.FileRecord]:
        # Filtrar por usuario y prefijo de ruta (simplificado)
        search_path = str(Path(relative_path))
        return self.db.query(models.FileRecord).filter(
            models.FileRecord.user_id == user_id,
            models.FileRecord.path.like(f"{search_path}%"),
            models.FileRecord.status == "active"
        ).all()

    def get_file_path(self, user_id: str, file_id: str) -> Optional[Path]:
        record = self._get_user_db_record(user_id, file_id)
        if not record:
            return None
        return storage_utils.sanitize_path(self.base_root, user_id, record.path)

    def move_to_trash(self, user_id: str, file_id: str) -> bool:
        record = self._get_user_db_record(user_id, file_id)
        if not record:
            return False
        
        current_path = storage_utils.sanitize_path(self.base_root, user_id, record.path)
        trash_dir = storage_utils.sanitize_path(self.base_root, user_id, "trash")
        
        if current_path and current_path.exists():
            new_path = trash_dir / record.name
            shutil.move(str(current_path), str(new_path))
            record.status = "trashed"
            record.path = f"trash/{record.name}"
            self.db.commit()
            return True
        return False

    def delete_permanently(self, user_id: str, file_id: str) -> bool:
        record = self._get_user_db_record(user_id, file_id)
        if not record:
            return False
        
        current_path = storage_utils.sanitize_path(self.base_root, user_id, record.path)
        if current_path and current_path.exists():
            os.remove(current_path)
        
        self.db.delete(record)
        self.db.commit()
        return True
