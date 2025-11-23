from json import JSONDecodeError
from pathlib import Path
from pydantic import BaseModel
from shutil import copy2

from .json_file_operations import JsonFileOperations

class PersistentJsonHandler(JsonFileOperations):
    
    def __init__(self, main_file_path: Path, backup_file_path: Path, default_data: BaseModel):
        self._main_file_path: Path = main_file_path
        self._backup_file_path: Path = backup_file_path
        self._default_data: BaseModel = default_data
        self._data: dict = default_data.model_dump() # is initialized with the default to prevent empty value
        
        self._setup_files()
    
    
    def _setup_files(self) -> None:
        if self._main_file_path.exists() and self._backup_file_path.exists():
            return
        
        if not self._main_file_path.exists():
            self._handle_file_restore()
        
        if not self._backup_file_path.exists():
            self._ensure_backup()
    
    
    def load_data(self) -> None:
        try:
            self._load_validate_and_synchronize()
        except JSONDecodeError:
            # put message in queue
            self._handle_file_restore()
    
    
    def get_data(self) -> dict:
        return self._data
    
    
    def set_data(self, new_data: dict) -> None:
        self._data = new_data
        self._save_data()
        self._ensure_backup()
    
    
    # helper methods below
    
    def _save_data(self) -> None:
        return super().perform_save(self._main_file_path, self._data)
    
    
    def _load_validate_and_synchronize(self) -> None:
        raw_json: dict = super().perform_load(self._main_file_path)
        self._data = self._default_data.model_validate(raw_json).model_dump(by_alias=True)
            
        if raw_json != self._data: # data changed
            self._save_data()
            self._ensure_backup()
    
    
    def _ensure_backup(self) -> None:
        backup_exists: bool = self._backup_file_path.exists()
        
        try:
            copy2(self._main_file_path, self._backup_file_path)
            
            if backup_exists:
                # put message in queue
                pass
        except Exception as e:
            # put message in queue
            pass
    
    
    def _handle_file_restore(self) -> None:
        if not self._backup_file_path.exists():
            # put message in queue
            self._reinitialize_main_file()
            self._reinitialize_backup_file()
            return
        
        try:
            self._main_file_path.unlink(missing_ok=True)
            self._load_backup()
            self._load_validate_and_synchronize()
            # put message in queue
        except JSONDecodeError:
            # put message in queue
            self._reinitialize_main_file()
            self._reinitialize_backup_file()
    
    
    def _reinitialize_main_file(self) -> None:
        try:
            self._set_default_value()
            self._main_file_path.unlink(missing_ok=True)
            self._create_main_file()
            # put message in queue
        except Exception as e:
            # put message in queue
            pass
    
    
    def _reinitialize_backup_file(self) -> None:
        try:
            self._backup_file_path.unlink(missing_ok=True)
            self._ensure_backup()
            # put message in queue
        except Exception as e:
            # put message in queue
            pass
    
    
    def _create_main_file(self) -> None:
        if not self._main_file_path.exists():
            self._save_data()
    
    
    def _load_backup(self) -> None:
        copy2(self._backup_file_path, self._main_file_path)
    
    
    def _set_default_value(self) -> None:
        self._data: dict = self._default_data.model_dump()