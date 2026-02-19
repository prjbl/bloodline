from pathlib import Path
from shutil import move, make_archive, rmtree
from typing import List, Tuple

from platformdirs import user_data_dir

from .directory import Directory
from file_io.json import MigrationJsonHandler

class MigrationPipeline:
    
    _MIGRATION_VERSIONS: List[dict] = [
        {
            "version": "0.9.0-beta",
            "root_dir": Path(user_data_dir(roaming=True)) / "Bloodline",
            "src_path": Path(user_data_dir(roaming=True)) / "Bloodline" / "0.9.0-beta",
            "required_files": ["ui_config.json", "save_file.sqlite"],
            "migration_method": "_migrate_v090_to_v0100"
        }
        #{
        #    "version": ...,
        #    "root_dir": ...,
        #    "src_path": ...,
        #    "required_files": ...,
        #    "migration_method": ...
        #}
    ]
    
    
    @classmethod
    def run_all_migrations(cls) -> None:
        pending_migrations: List[dict] = cls._get_pending_migrations()
        
        if not pending_migrations:
            return
        
        cls._archive_legacy_backup(pending_migrations[-1])
        
        for legacy_data in pending_migrations:
            method_name: str = legacy_data.get("migration_method")
            getattr(cls, method_name)(legacy_data)
        
        for legacy_data in pending_migrations:
            cls._cleanup_legacy_data(legacy_data.get("root_dir"))
    
    
    @staticmethod
    def _archive_legacy_backup(legacy_data: dict) -> None:
        Directory.create_archive_dir()
        archive_path: Path = Directory.get_archive_path()
        
        backup_name: str = legacy_data.get("version")
        src_path: Path = legacy_data.get("src_path")
        dst_path: Path = archive_path / backup_name
        
        make_archive(
            base_name=str(dst_path),
            format="zip",
            root_dir=str(src_path)
        )
    
    
    # version specific method below
    
    @classmethod
    def _migrate_v090_to_v0100(cls, legacy_data: dict) -> None:
        src_path: Path = legacy_data.get("src_path")
        dst_path: Path = Directory.get_persistent_data_path()
        backup_path: Path = Directory.get_backup_path()
        
        cls._move_all_data(src_path, dst_path)
        
        entries_to_rename: List[Tuple[str, str, Path]] = [
            ("save_file.sqlite", "stats.sqlite", dst_path),
            ("save_file.sqlite.bak", "stats.sqlite.bak", backup_path),
            ("update_status.json", "update_state.json", dst_path),
            ("update_status.json.bak", "update_state.json.bak", backup_path)
        ]
        cls._rename_entries(entries_to_rename)
        
        ui_config: dict | None = MigrationJsonHandler.load_raw(dst_path / "ui_config.json")
        
        if ui_config is None:
            return
        
        MigrationJsonHandler.save_raw(dst_path / "window_state.json", ui_config.get("window"))
        MigrationJsonHandler.save_raw(dst_path / "theme.json", ui_config.get("theme"))
        
        entries_to_remove: List[Path] = [
            dst_path / "ui_config.json",
            backup_path / "ui_config.json.bak"
        ]
        cls._remove_entries(entries_to_remove)
    
    
    # helper methods below
    
    @classmethod
    def _get_pending_migrations(cls) -> List[dict]:
        pending_migrations: List[dict] = []
        
        for legacy_data in cls._MIGRATION_VERSIONS:
            src_path: Path = legacy_data.get("src_path")
            
            if not src_path.exists():
                continue
            
            matching_files: bool = all((src_path / file).exists() for file in legacy_data.get("required_files"))
            
            if matching_files:
                pending_migrations.append(legacy_data)
        return pending_migrations
    
    
    @staticmethod
    def _move_all_data(src_path: Path, dst_path: Path) -> None:
        for item in src_path.iterdir():
            target_item: Path = dst_path / item.name
            
            if target_item.exists():
                if target_item.is_dir():
                    rmtree(str(target_item))
                else:
                    target_item.unlink()
            
            move(str(item), str(target_item))
    
    
    @staticmethod
    def _rename_entries(entries: List[Tuple[str, str, Path]]) -> None:
        for old_name, new_name, dir in entries:
            old_path: Path = dir / old_name
            new_path: Path = dir / new_name
            
            if old_path.exists():
                old_path.replace(str(new_path))
    
    
    @staticmethod
    def _remove_entries(entries: List[Path]) -> None:
        for item in entries:
            if item.is_dir():
                rmtree(str(item))
            else:
                item.unlink()
    
    
    @staticmethod
    def _cleanup_legacy_data(legacy_root_dir: Path) -> None:
        if not legacy_root_dir.exists():
            return
        
        curr_dir: Path = Directory.get_persistent_data_path()
        
        if legacy_root_dir.resolve() != curr_dir.resolve():
            rmtree(str(legacy_root_dir))