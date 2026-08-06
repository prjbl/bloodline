from pathlib import Path

from platformdirs import user_config_dir, user_data_dir, user_state_dir, user_documents_dir

from .metadata import Metadata

class Directory:
    _BACKUP_DIR: str = "backups"
    _ARCHIVE_DIR: str = "_archive"
    _LOGS_DIR: str = "logs"
    _EXPORT_DIR: str = "exports"
    
    # Windows: AppData/Roaming/
    # Linux: ~/.config/
    ROAMING_DATA_PATH: Path = Path(user_config_dir(roaming=True)) / Metadata.DIR_AUTHOR / Metadata.DIR_APP_NAME
    
    # Windows: AppData/Local/
    # Linux: ~/.local/share/
    LOCAL_DATA_PATH: Path = Path(user_data_dir(roaming=False)) / Metadata.DIR_AUTHOR / Metadata.DIR_APP_NAME
    BACKUP_PATH: Path = LOCAL_DATA_PATH / _BACKUP_DIR
    ARCHIVE_PATH: Path = LOCAL_DATA_PATH / _ARCHIVE_DIR
    
    # Linux: ~/.local/state/
    STATE_DATA_PATH: Path = Path(user_state_dir()) / Metadata.DIR_AUTHOR / Metadata.DIR_APP_NAME
    
    # Windows: AppData/Local/
    # Linux: ~/.local/state/
    LOGS_PATH: Path = STATE_DATA_PATH / _LOGS_DIR if Metadata.OS_IS_LINUX else LOCAL_DATA_PATH / _LOGS_DIR
    
    # Windows & Linux: User documents
    DOCS_DATA_PATH: Path = Path(user_documents_dir()) / Metadata.DIR_AUTHOR / Metadata.DIR_APP_NAME
    EXPORT_PATH: Path = DOCS_DATA_PATH / _EXPORT_DIR
    
    
    @classmethod
    def setup_all_dirs(cls) -> None:
        dirs: set = {
            cls.ROAMING_DATA_PATH,
            cls.LOCAL_DATA_PATH,
            cls.BACKUP_PATH,
            cls.LOGS_PATH,
            cls.DOCS_DATA_PATH
        }
        
        if Metadata.OS_IS_LINUX:
            dirs.add(cls.STATE_DATA_PATH)
        
        for dir in dirs:
            dir.mkdir(parents=True, exist_ok=True)
    
    
    @classmethod
    def create_archive_dir(cls) -> None:
        cls.ARCHIVE_PATH.mkdir(parents=True, exist_ok=True)
    
    
    @classmethod
    def create_export_dir(cls) -> None:
        cls.EXPORT_PATH.mkdir(parents=True, exist_ok=True)


class _PathDef:
    
    def __init__(self, file_name: str, has_backup: bool = True, provide_local: bool = False, provide_docs: bool = False):
        self._file_name: str = file_name.replace("_", "-") if Metadata.OS_IS_LINUX else file_name
        
        self._main_file_path: Path = Directory.ROAMING_DATA_PATH / self._file_name
        self._backup_file_path: Path | None = Directory.BACKUP_PATH / f"{self._file_name}.bak" if has_backup else None
        self._local_file_path: Path | None = Directory.LOCAL_DATA_PATH / self._file_name if provide_local else None
        self._state_file_path: Path | None = Directory.STATE_DATA_PATH / self._file_name if Metadata.OS_IS_LINUX else None
        self._docs_file_path: Path | None = Directory.DOCS_DATA_PATH / self._file_name if provide_docs else None
    
    
    @property
    def file_name(self) -> str:
        return self._file_name
    
    
    @property
    def main_file_path(self) -> Path:
        return self._main_file_path
    
    
    @property
    def backup_file_path(self) -> Path | None:
        return self._backup_file_path
    
    
    @property
    def local_file_path(self) -> Path | None:
        return self._local_file_path
    
    
    @property
    def state_file_path(self) -> Path | None:
        return self._state_file_path
    
    
    @property
    def docs_file_path(self) -> Path | None:
        return self._docs_file_path


class SystemFiles:
    BLOODLINE_METADATA: _PathDef = _PathDef(
        file_name=".bloodline.metadata",
        has_backup=False,
        provide_local=True,
        provide_docs=True
    )
    HOTKEYS: _PathDef = _PathDef("hotkeys.json")
    SETTINGS: _PathDef = _PathDef("settings.json")
    STATS: _PathDef = _PathDef("stats.sqlite")
    THEME: _PathDef = _PathDef("theme.json")
    UPDATE_STATE: _PathDef = _PathDef("update_state.json")
    WINDOW_STATE: _PathDef = _PathDef("window_state.json")