from __future__ import annotations

from typing import override

from file_io.json import SystemJsonHandler
from infrastructure.config import WSectionKeys as SectionKeys, WindowKeys, SystemFiles
from infrastructure.interfaces import IWindowManager
from schemas.definitions import WindowModel

class WindowManager(IWindowManager):
    
    _instance: WindowManager | None = None
    _sys_json_handler: SystemJsonHandler
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            cls._instance._sys_json_handler = SystemJsonHandler(
                main_file_path=SystemFiles.WINDOW_STATE.main_file_path,
                backup_file_path=SystemFiles.WINDOW_STATE.backup_file_path,
                validation_model=WindowModel()
            )
        return cls._instance
    
    
    @override
    def set_toplevel_enabled(self, new_enable_state: bool) -> bool:
        return self._set_toplevel_state(new_enable_state, WindowKeys.ENABLED)
    
    
    @override
    def set_toplevel_locked(self, new_lock_state: bool) -> bool:
        return self._set_toplevel_state(new_lock_state, WindowKeys.LOCKED)
    
    
    def get_root_props(self) -> dict:
        return self._sys_json_handler.data[SectionKeys.ROOT]
    
    
    def get_toplevel_props(self) -> dict:
        return self._sys_json_handler.data[SectionKeys.TOPLEVEL]
    
    
    def set_root_props(self, new_geometry: str, new_max_state: bool) -> None:
        window_state: dict = self._sys_json_handler.data
        
        old_geometry: str = window_state[SectionKeys.ROOT][WindowKeys.GEOMETRY]
        old_max_state: bool = window_state[SectionKeys.ROOT][WindowKeys.MAXIMIZED]
        
        if new_geometry == old_geometry and new_max_state == old_max_state:
            return
        
        if new_max_state != old_max_state:
            window_state[SectionKeys.ROOT][WindowKeys.MAXIMIZED] = new_max_state
        if new_geometry != old_geometry and not new_max_state: # only triggered if geometry changed and state is not maximized
            window_state[SectionKeys.ROOT][WindowKeys.GEOMETRY] = new_geometry
        
        self._sys_json_handler.set_data(window_state)
    
    
    def set_toplevel_props(self, new_geometry: str) -> None:
        window_state: dict = self._sys_json_handler.data
        
        old_geometry: str = window_state[SectionKeys.TOPLEVEL][WindowKeys.GEOMETRY]
        
        if new_geometry == old_geometry:
            return
        window_state[SectionKeys.TOPLEVEL][WindowKeys.GEOMETRY] = new_geometry
        
        self._sys_json_handler.set_data(window_state)
    
    
    # helper methods below
    
    def _set_toplevel_state(self, new_state: bool, window_key: str) -> bool:
        window_state: dict = self._sys_json_handler.data
        
        old_state: bool = window_state[SectionKeys.TOPLEVEL][window_key]
        
        if new_state == old_state:
            return False
        window_state[SectionKeys.TOPLEVEL][window_key] = new_state
        
        self._sys_json_handler.set_data(window_state)
        return True