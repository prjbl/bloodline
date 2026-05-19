from json import JSONDecodeError
from logging import Logger, getLogger
from pathlib import Path
from shutil import copy2
from typing import override

from pydantic import BaseModel

from .json_file_operations import JsonFileOperations
from infrastructure import MessageHub
from infrastructure.interfaces import ISystemBackupStrategy, ISystemJsonHandler

_msg_provider: MessageHub = MessageHub()
_logger: Logger = getLogger(__name__)

class _ActiveBackup(ISystemBackupStrategy):
    
    def __init__(self, sys_json_handler: ISystemJsonHandler, backup_file_path: Path):
        self._sys_json_handler: ISystemJsonHandler = sys_json_handler
        self._backup_file_path: Path = backup_file_path
        
        self._backup_file_name: str = backup_file_path.name
    
    
    @override
    def backup_exists(self) -> bool:
        return self._backup_file_path.exists()
    
    
    @override
    def sync_backup(self) -> None:
        main_file_path: Path = self._sys_json_handler._file_path
        main_file_name: str = self._sys_json_handler._file_name
        
        try:
            copy2(main_file_path, self._backup_file_path)
        except Exception as e:
            _msg_provider.invoke(
                f"An unexpected error occurred while loading the backup to the file \"{main_file_name}\".\n"
                f"Exception: {e}", "error"
            )
            _logger.exception(f"System file backup load failed: \"{self._backup_file_name}\" -> \"{main_file_name}\"")
    
    
    @override
    def handle_file_restore(self) -> None:
        if not self.backup_exists():
            _msg_provider.invoke("No backup could be found. Both files will be re-initialized", "error")
            self._sys_json_handler._reinitialize_main_file()
            self._reinitialize_backup_file()
            return
        
        main_file_path: Path = self._sys_json_handler._file_path
        
        try:
            main_file_path.unlink(missing_ok=True)
            self._load_backup()
            self._sys_json_handler._load_validate_and_synchronize()
            _msg_provider.invoke(f"Loading the backup from \"{self._backup_file_name}\" was successful", "success")
        except JSONDecodeError:
            _msg_provider.invoke(f"The file \"{self._backup_file_name}\" is corrupted. Both files will be re-initialized", "error")
            self._sys_json_handler._reinitialize_main_file()
            self._reinitialize_backup_file()
    
    
    # helper methods below
    
    def _reinitialize_backup_file(self) -> None:
        try:
            self._backup_file_path.unlink(missing_ok=True)
            self.sync_backup()
            _msg_provider.invoke(f"The file \"{self._backup_file_name}\" was re-initialized successfully", "success")
        except Exception as e:
            _msg_provider.invoke(
                f"An unexpected error occurred while re-initializing the file \"{self._backup_file_name}\".\n"
                f"Exception: {e}", "error"
            )
            _logger.exception(f"System file backup reset failed (\"{self._backup_file_name}\")")
    
    
    def _load_backup(self) -> None:
        main_file_path: Path = self._sys_json_handler._file_path
        copy2(self._backup_file_path, main_file_path)


class _NoBackup(ISystemBackupStrategy):
    
    def __init__(self, sys_json_handler: ISystemJsonHandler):
        self._sys_json_handler: ISystemJsonHandler = sys_json_handler
    
    
    @override
    def backup_exists(self) -> bool:
        return False
    
    
    @override
    def sync_backup(self) -> None:
        pass
    
    
    @override
    def handle_file_restore(self) -> None:
        self._sys_json_handler._reinitialize_main_file()


class SystemJsonHandler(JsonFileOperations, ISystemJsonHandler):
    
    def __init__(self, main_file_path: Path, validation_model: BaseModel, backup_file_path: Path | None = None):
        self._main_file_path: Path = main_file_path
        self._validation_model: BaseModel = validation_model
        self._data: dict = validation_model.model_dump() # is initialized with the default to prevent empty value
        self._backup_strategy: _ActiveBackup | _NoBackup = (
            _ActiveBackup(self, backup_file_path) if backup_file_path is not None else _NoBackup(self)
        )
        
        self._main_file_name: str = main_file_path.name
        
        self._setup_files()
        self._load_data()
    
    
    @override
    @property
    def _file_path(self) -> Path:
        return self._main_file_path
    
    
    @override
    @property
    def _file_name(self) -> str:
        return self._main_file_name
    
    
    @override
    def _load_validate_and_synchronize(self) -> None:
        raw_json: dict = self._perform_load(self._main_file_path)
        self._data = self._validation_model.model_validate(raw_json).model_dump(by_alias=True)
        
        if raw_json != self._data: # data changed
            self._save_data()
            self._backup_strategy.sync_backup()
    
    
    @override
    def _create_main_file(self) -> None:
        self._save_data()
    
    
    @override
    def _reinitialize_main_file(self) -> None:
        try:
            self._set_default_value()
            self._main_file_path.unlink(missing_ok=True)
            self._create_main_file()
            _msg_provider.invoke(f"The file \"{self._main_file_name}\" was re-initialized successfully", "success")
        except Exception as e:
            _msg_provider.invoke(
                f"An unexpected error occurred while re-initializing the file \"{self._main_file_name}\".\n"
                f"Exception: {e}", "error"
            )
            _logger.exception(f"System file reset failed (\"{self._main_file_name}\")")
    
    
    def _setup_files(self) -> None:
        main_file_exists: bool = self._main_file_path.exists()
        backup_file_exists: bool = self._backup_strategy.backup_exists()
        
        if main_file_exists and backup_file_exists:
            return
        
        if not main_file_exists and not backup_file_exists:
            self._create_main_file()
            self._backup_strategy.sync_backup()
            return
        
        if not main_file_exists:
            self._backup_strategy.handle_file_restore()
        
        if not backup_file_exists:
            self._backup_strategy.sync_backup()
    
    
    def _load_data(self) -> None:
        try:
            self._load_validate_and_synchronize()
        except JSONDecodeError:
            backup_file_exists: bool = self._backup_strategy.backup_exists()
            
            if not backup_file_exists:
                _msg_provider.invoke(f"The file \"{self._main_file_name}\" is corrupted. It will be re-initialized", "error")
            else:
                _msg_provider.invoke(f"The file \"{self._main_file_name}\" is corrupted. An attempt is made to load the last backup", "error")
            
            self._backup_strategy.handle_file_restore()
    
    
    @property
    def data(self) -> dict:
        return self._data
    
    
    def set_data(self, new_data: dict) -> None:
        self._data = new_data
        self._save_data()
        self._backup_strategy.sync_backup()
    
    
    # helper methods below
    
    def _save_data(self) -> None:
        self._perform_save(self._main_file_path, self._data)
    
    
    def _set_default_value(self) -> None:
        self._data: dict = self._validation_model.model_dump()