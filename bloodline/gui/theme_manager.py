from __future__ import annotations

from typing import override, Callable

from file_io.json import SystemJsonHandler
from infrastructure.config import TSectionKeys as SectionKeys, SystemFiles
from infrastructure.interfaces import IThemeManager
from schemas.definitions import ThemeModel

class ThemeManager(IThemeManager):
    
    _instance: ThemeManager | None = None
    _sys_json_handler: SystemJsonHandler | None = None
    _reload_widgets: Callable[[int], None] | None = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            cls._instance._sys_json_handler = SystemJsonHandler(
                main_file_path=SystemFiles.THEME.main_file_path,
                backup_file_path=SystemFiles.THEME.backup_file_path,
                validation_model=ThemeModel()
            )
        return cls._instance
    
    
    @override
    def get_theme(self) -> dict:
        return self._sys_json_handler.data
    
    
    @override
    def set_theme(self, loaded_theme: dict) -> None:
        self._sys_json_handler.set_data(loaded_theme)
        self._reload_widgets(50)
    
    
    def link_callback(self, callback_method: Callable[[int], None]) -> None:
        self._reload_widgets = callback_method
    
    
    def get_colors(self) -> dict:
        return self._sys_json_handler.data[SectionKeys.COLORS]
    
    
    def get_root_font_props(self) -> dict:
        shared_font_props: dict = self._get_shared_props(self._get_font_props())
        root_specific_props: dict = self._get_font_props()[SectionKeys.ROOT]
        return {**shared_font_props, **root_specific_props} # unpack and merge
    
    
    def get_toplevel_font_props(self) -> dict:
        shared_font_props: dict = self._get_shared_props(self._get_font_props())
        toplevel_specific_props: dict = self._get_font_props()[SectionKeys.TOPLEVEL]
        return {**shared_font_props, **toplevel_specific_props}
    
    
    def get_root_widget_props(self) -> dict:
        shared_widget_props: dict = self._get_shared_props(self._get_widget_props())
        root_specific_props: dict = self._get_widget_props()[SectionKeys.ROOT]
        return {**shared_widget_props, **root_specific_props}
    
    
    def get_toplevel_widget_props(self) -> dict:
        share_widget_props: dict = self._get_shared_props(self._get_widget_props())
        toplevel_specific_props: dict = self._get_widget_props()[SectionKeys.TOPLEVEL]
        return {**share_widget_props, **toplevel_specific_props}
    
    
    # helper methods below
    
    @staticmethod
    def _get_shared_props(category_props: dict) -> dict:
        shared_props: dict = {
            key: value for key, value in category_props.items() if not isinstance(value, dict)
        }
        return shared_props
    
    
    def _get_font_props(self) -> dict:
        return self._sys_json_handler.data[SectionKeys.FONT]
    
    
    def _get_widget_props(self) -> dict:
        return self._sys_json_handler.data[SectionKeys.WIDGETS]