from __future__ import annotations

from typing import override

from file_io.json import SystemJsonHandler
from infrastructure.config import WSectionKeys as SectionKeys, WindowKeys, SystemFiles
from infrastructure.interfaces import IWindowManager
from schemas.definitions import WindowModel

class WindowManager(IWindowManager):
    
    _instance: WindowManager | None = None
    _sys_json_handler: SystemJsonHandler | None = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            cls._instance._sys_json_handler = SystemJsonHandler(
                main_file_path=SystemFiles.WINDOW_STATE.main_file_path,
                backup_file_path=SystemFiles.WINDOW_STATE.backup_file_path,
                default_data=WindowModel()
            )
            cls._instance._sys_json_handler.load_data()
        return cls._instance
    
    
    @override
    def set_toplevel_locked(self, new_lock_state: bool) -> bool:
        window_state: dict = self._sys_json_handler.get_data()
        
        old_lock_state: bool = window_state.get(SectionKeys.TOPLEVEL).get(WindowKeys.LOCKED)
        
        if new_lock_state == old_lock_state:
            return False
        window_state[SectionKeys.TOPLEVEL][WindowKeys.LOCKED] = new_lock_state
        
        self._sys_json_handler.set_data(window_state)
        return True
    
    
    def get_root_props(self) -> dict:
        return self._sys_json_handler.get_data().get(SectionKeys.ROOT)
    
    
    def get_toplevel_props(self) -> dict:
        return self._sys_json_handler.get_data().get(SectionKeys.TOPLEVEL)
    
    
    def set_root_props(self, new_geometry: str, new_max_state: bool) -> None:
        window_state: dict = self._sys_json_handler.get_data()
        
        old_geometry: str = window_state.get(SectionKeys.ROOT).get(WindowKeys.GEOMETRY)
        old_max_state: bool = window_state.get(SectionKeys.ROOT).get(WindowKeys.MAXIMIZED)
        
        if new_geometry == old_geometry and new_max_state == old_max_state:
            return
        
        if new_max_state != old_max_state:
            window_state[SectionKeys.ROOT][WindowKeys.MAXIMIZED] = new_max_state
        if new_geometry != old_geometry and not new_max_state: # only triggered if geometry changed and state is not maximized
            window_state[SectionKeys.ROOT][WindowKeys.GEOMETRY] = new_geometry
        
        self._sys_json_handler.set_data(window_state)
    
    
    def set_toplevel_props(self, new_geometry: str) -> None:
        window_state: dict = self._sys_json_handler.get_data()
        
        old_geometry: str = window_state.get(SectionKeys.TOPLEVEL).get(WindowKeys.GEOMETRY)
        
        if new_geometry == old_geometry:
            return
        window_state[SectionKeys.TOPLEVEL][WindowKeys.GEOMETRY] = new_geometry
        
        self._sys_json_handler.set_data(window_state)