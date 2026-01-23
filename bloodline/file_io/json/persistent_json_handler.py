from json import JSONDecodeError
from pathlib import Path
from shutil import copy2

from pydantic import BaseModel

from .json_file_operations import JsonFileOperations
from infrastructure import MessageHub

class PersistentJsonHandler(JsonFileOperations):
    
    def __init__(self, main_file_path: Path, backup_file_path: Path, default_data: BaseModel):
        self._main_file_path: Path = main_file_path
        self._backup_file_path: Path = backup_file_path
        self._default_data: BaseModel = default_data
        self._data: dict = default_data.model_dump() # is initialized with the default to prevent empty value
        
        self._msg_provider: MessageHub = MessageHub()
        
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
            self._msg_provider.invoke(f"The file '{self._main_file_path}' is corrupted. An attempt is made to load the last backup.", "error")
            self._handle_file_restore()
    
    
    def get_data(self) -> dict:
        return self._data
    
    
    def set_data(self, new_data: dict) -> None:
        self._data = new_data
        self._save_data()
        self._ensure_backup()
    
    
    # helper methods below
    
    def _save_data(self) -> None:
        return self._perform_save(self._main_file_path, self._data)
    
    
    def _load_validate_and_synchronize(self) -> None:
        raw_json: dict = self._perform_load(self._main_file_path)
        self._data = self._default_data.model_validate(raw_json).model_dump(by_alias=True)
            
        if raw_json != self._data: # data changed
            self._save_data()
            self._ensure_backup()
    
    
    def _ensure_backup(self) -> None:
        try:
            copy2(self._main_file_path, self._backup_file_path)
        except Exception as e:
            self._msg_provider.invoke(f"An unexpected error occured while backuping the '{self._main_file_path}'. Exception: {e}", "error")
    
    
    def _handle_file_restore(self) -> None:
        if not self._backup_file_path.exists():
            self._msg_provider.invoke("No backup could be found. Both files will be re-initialized", "error")
            self._reinitialize_main_file()
            self._reinitialize_backup_file()
            return
        
        try:
            self._main_file_path.unlink(missing_ok=True)
            self._load_backup()
            self._load_validate_and_synchronize()
            self._msg_provider.invoke(f"Loading backup from '{self._backup_file_path}' was successful", "success")
        except JSONDecodeError:
            self._msg_provider.invoke(f"The '{self._backup_file_path}' is also corrupted. Both files will be re-initialized", "error")
            self._reinitialize_main_file()
            self._reinitialize_backup_file()
    
    
    def _reinitialize_main_file(self) -> None:
        try:
            self._set_default_value()
            self._main_file_path.unlink(missing_ok=True)
            self._create_main_file()
            self._msg_provider.invoke(f"The '{self._main_file_path}' was re-initialized successfully", "success")
        except Exception as e:
            self._msg_provider.invoke(f"An unexpected error occured while re-initializing the '{self._main_file_path}'. Exception: {e}", "error")
    
    
    def _reinitialize_backup_file(self) -> None:
        try:
            self._backup_file_path.unlink(missing_ok=True)
            self._ensure_backup()
            self._msg_provider.invoke(f"The '{self._backup_file_path}' was re-initialized successfully", "success")
        except Exception as e:
            self._msg_provider.invoke(f"An unexpected error occured while re-initializing the '{self._backup_file_path}'. Exception: {e}", "error")
    
    
    def _create_main_file(self) -> None:
        if not self._main_file_path.exists():
            self._save_data()
    
    
    def _load_backup(self) -> None:
        copy2(self._backup_file_path, self._main_file_path)
    
    
    def _set_default_value(self) -> None:
        self._data: dict = self._default_data.model_dump()