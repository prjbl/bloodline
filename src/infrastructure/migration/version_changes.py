from pathlib import Path
from shutil import move, rmtree
from typing import List, Tuple

from .legacy_data import LegacyData
from file_io.json import MigrationJsonHandler

class VersionChanges:
    
    @classmethod
    def migrate_v090_to_091(cls, legacy_data: LegacyData, next_legacy_data: LegacyData) -> None:
        # Roaming
        old_roaming_path: Path = legacy_data.roaming_data_path
        new_roaming_path: Path = next_legacy_data.roaming_data_path
        old_backup_path: Path = next_legacy_data.roaming_data_path / "backups"
        new_backup_path: Path = next_legacy_data.local_data_path / "backups"
        
        cls._move_all_data(old_roaming_path, new_roaming_path)
        cls._move_all_data(old_backup_path, new_backup_path)
        
        entries_to_rename: List[Tuple[str, str, Path]] = [
            ("save_file.sqlite", "stats.sqlite", new_roaming_path),
            ("save_file.sqlite.bak", "stats.sqlite.bak", new_backup_path),
            ("update_status.json", "update_state.json", new_roaming_path),
            ("update_status.json.bak", "update_state.json.bak", new_backup_path)
        ]
        cls._rename_entries(entries_to_rename)
        
        def split_config_data(src_path: Path, dst_path: Path) -> None:
            raw_config_data: dict | None = MigrationJsonHandler.load_raw(src_path)
            
            if raw_config_data is None:
                return
            
            file_suffix: str = ".bak" if src_path.suffix == ".bak" else ""
            window_data: dict | None = raw_config_data.get("window")
            theme_data: dict | None = raw_config_data.get("theme")
            
            if window_data is not None:
                MigrationJsonHandler.save_data(dst_path / f"window_state.json{file_suffix}", window_data)
            if theme_data is not None:
                MigrationJsonHandler.save_data(dst_path / f"theme.json{file_suffix}", theme_data)
        
        split_config_data(new_roaming_path / "ui_config.json", new_roaming_path)
        split_config_data(new_backup_path / "ui_config.json.bak", new_backup_path)
        
        # User documents
        old_docs_path: Path = legacy_data.docs_data_path
        new_docs_path: Path = next_legacy_data.docs_data_path
        
        cls._move_all_data(old_docs_path, new_docs_path)
        
        # Clear old files and directories
        entries_to_delete: List[Path] = [
            new_roaming_path / "ui_config.json",
            new_backup_path / "ui_config.json.bak",
            new_docs_path / "exports",
            old_roaming_path.parent,
            old_backup_path,
            old_docs_path
        ]
        cls._delete_entries(entries_to_delete)
    
    
    # helper methods below
    
    @staticmethod
    def _move_all_data(src_path: Path, dst_path: Path) -> None:
        for item in src_path.iterdir(): # iterdir may not work for unix style hidden files
            target_item: Path = dst_path / item.name
            
            if target_item.exists():
                if target_item.is_dir():
                    rmtree(target_item)
                else:
                    target_item.unlink()
            
            move(item, target_item)
    
    
    @staticmethod
    def _rename_entries(entries: List[Tuple[str, str, Path]]) -> None:
        for old_name, new_name, dir in entries:
            old_path: Path = dir / old_name
            new_path: Path = dir / new_name
            
            if old_path.exists():
                old_path.replace(new_path)
    
    
    @staticmethod
    def _delete_entries(entries: List[Path]) -> None:
        for item in entries:
            if item.is_dir():
                rmtree(item)
            else:
                item.unlink()