from __future__ import annotations

from pathlib import Path
from typing import override

from file_io.json import PersistentJsonHandler
from infrastructure import Directory
from infrastructure.interfaces import IWindowManager
from schemas import WindowModel, WSectionKeys, WindowKeys

class WindowManager(IWindowManager):
    
    _instance: WindowManager | None = None
    _pers_json_handler: PersistentJsonHandler | None = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            cls._instance._pers_json_handler = PersistentJsonHandler(
                main_file_path=cls._instance._STATE_FILE_PATH,
                backup_file_path=cls._instance._BACKUP_FILE_PATH,
                default_data=WindowModel()
            )
            cls._instance._pers_json_handler.load_data()
        return cls._instance
    
    
    _STATE_FILE: str = "window_state.json"
    _BACKUP_FILE: str = f"{_STATE_FILE}.bak"
    _STATE_FILE_PATH: Path = Directory.get_persistent_data_path() / _STATE_FILE
    _BACKUP_FILE_PATH: Path = Directory.get_backup_path() / _BACKUP_FILE
    
    
    @override
    def set_toplevel_locked(self, new_lock_state: bool) -> bool:
        window_state: dict = self._pers_json_handler.get_data()
        
        old_lock_state: bool = window_state.get(WSectionKeys.TOPLEVEL).get(WindowKeys.LOCKED)
        
        if new_lock_state == old_lock_state:
            return False
        window_state[WSectionKeys.TOPLEVEL][WindowKeys.LOCKED] = new_lock_state
        
        self._pers_json_handler.set_data(window_state)
        return True
    
    
    def get_root_props(self) -> dict:
        return self._pers_json_handler.get_data().get(WSectionKeys.ROOT)
    
    
    def get_toplevel_props(self) -> dict:
        return self._pers_json_handler.get_data().get(WSectionKeys.TOPLEVEL)
    
    
    def set_root_props(self, new_geometry: str, new_max_state: bool) -> None:
        window_state: dict = self._pers_json_handler.get_data()
        
        old_geometry: str = window_state.get(WSectionKeys.ROOT).get(WindowKeys.GEOMETRY)
        old_max_state: bool = window_state.get(WSectionKeys.ROOT).get(WindowKeys.MAXIMIZED)
        
        if new_geometry == old_geometry and new_max_state == old_max_state:
            return
        
        if new_max_state != old_max_state:
            window_state[WSectionKeys.ROOT][WindowKeys.MAXIMIZED] = new_max_state
        if new_geometry != old_geometry and not new_max_state: # only triggered if geometry changed and state is not maximized
            window_state[WSectionKeys.ROOT][WindowKeys.GEOMETRY] = new_geometry
        
        self._pers_json_handler.set_data(window_state)
    
    
    def set_toplevel_props(self, new_geometry: str) -> None:
        window_state: dict = self._pers_json_handler.get_data()
        
        old_geometry: str = window_state.get(WSectionKeys.TOPLEVEL).get(WindowKeys.GEOMETRY)
        
        if new_geometry == old_geometry:
            return
        window_state[WSectionKeys.TOPLEVEL][WindowKeys.GEOMETRY] = new_geometry
        
        self._pers_json_handler.set_data(window_state)