from __future__ import annotations

from pathlib import Path
from typing import override

from file_io.json import PersistentJsonHandler
from infrastructure import Directory
from infrastructure.interfaces import IThemeManager
from schemas import ThemeModel, TSectionKeys

class ThemeManager(IThemeManager):
    
    _instance: ThemeManager | None = None
    _pers_json_handler: PersistentJsonHandler | None = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            cls._instance._pers_json_handler = PersistentJsonHandler(
                main_file_path=cls._instance._THEME_FILE_PATH,
                backup_file_path=cls._instance._BACKUP_FILE_PATH,
                default_data=ThemeModel()
            )
            cls._instance._pers_json_handler.load_data()
        return cls._instance
    
    
    _THEME_FILE: str = "theme.json"
    _BACKUP_FILE: str = f"{_THEME_FILE}.bak"
    _THEME_FILE_PATH: Path = Directory.get_persistent_data_path() / _THEME_FILE
    _BACKUP_FILE_PATH: Path = Directory.get_backup_path() / _BACKUP_FILE
    
    
    @override
    def get_theme(self) -> dict:
        return self._pers_json_handler.get_data()
    
    
    @override
    def set_theme(self, loaded_theme: dict) -> None:
        self._pers_json_handler.set_data(loaded_theme)
    
    
    def get_colors(self) -> dict:
        return self._pers_json_handler.get_data().get(TSectionKeys.COLORS)
    
    
    def get_root_font_props(self) -> dict:
        shared_font_props: dict = self._get_shared_props(self._get_font_props())
        root_specific_props: dict = self._get_font_props().get(TSectionKeys.ROOT)
        return {**shared_font_props, **root_specific_props} # unpack and merge
    
    
    def get_toplevel_font_props(self) -> dict:
        shared_font_props: dict = self._get_shared_props(self._get_font_props())
        toplevel_specific_props: dict = self._get_font_props().get(TSectionKeys.TOPLEVEL)
        return {**shared_font_props, **toplevel_specific_props}
    
    
    def get_root_widget_props(self) -> dict:
        shared_widget_props: dict = self._get_shared_props(self._get_widget_props())
        root_specific_props: dict = self._get_widget_props().get(TSectionKeys.ROOT)
        return {**shared_widget_props, **root_specific_props}
    
    
    def get_toplevel_widget_props(self) -> dict:
        share_widget_props: dict = self._get_shared_props(self._get_widget_props())
        toplevel_specific_props: dict = self._get_widget_props().get(TSectionKeys.TOPLEVEL)
        return {**share_widget_props, **toplevel_specific_props}
    
    
    # helper methods below
    
    @staticmethod
    def _get_shared_props(category_props: dict) -> dict:
        shared_props: dict = {
            key: value for key, value in category_props.items() if not isinstance(value, dict)
        }
        return shared_props
    
    
    def _get_font_props(self) -> dict:
        return self._pers_json_handler.get_data().get(TSectionKeys.FONT)
    
    
    def _get_widget_props(self) -> dict:
        return self._pers_json_handler.get_data().get(TSectionKeys.WIDGETS)