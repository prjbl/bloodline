from pathlib import Path
from shutil import move, make_archive, rmtree
from typing import List, Tuple

from platformdirs import user_data_dir, user_documents_dir

from .directory import Directory
from file_io.json import MigrationJsonHandler

class _LegacyData:
    
    def __init__(
        self,
        version: str,
        migration_method: str,
        roaming_dir: str,
        docs_dir: str,
        roaming_src: str | None = None,
        docs_src: str | None = None,
        roaming_backup: bool = True,
        docs_backup: bool = True,
        metadata: str | None = None,
        alt_signature: List[str] | None = None
    ):
        self._version: str = version
        self._migration_method: str = migration_method
        self._roaming_path: Path = Path(user_data_dir(roaming=True)) / roaming_dir
        self._docs_path: Path = Path(user_documents_dir()) / docs_dir
        self._roaming_src_path: Path = self._roaming_path / roaming_src if roaming_src is not None else self._roaming_path
        self._docs_src_path: Path = self._docs_path / docs_src if docs_src is not None else self._docs_path
        self._roaming_backup: bool = roaming_backup
        self._docs_backup: bool = docs_backup
        self._metadata: str | None = metadata
        self._alt_signature: List[str] | None = alt_signature
    
    
    def get_version(self) -> str:
        return self._version
    
    
    def get_migration_method(self) -> str:
        return self._migration_method
    
    
    def get_roaming_path(self) -> Path:
        return self._roaming_path
    
    
    def get_docs_path(self) -> Path:
        return self._docs_path
    
    
    def get_roaming_src_path(self) -> Path | None:
        return self._roaming_src_path
    
    
    def get_docs_src_path(self) -> Path | None:
        return self._docs_src_path
    
    
    def roaming_backup_required(self) -> bool:
        return self._roaming_backup
    
    
    def docs_backup_required(self) -> bool:
        return self._docs_backup
    
    
    def get_metadata(self) -> str | None:
        return self._metadata
    
    
    def get_alt_signature(self) -> List[str] | None:
        return self._alt_signature


class MigrationPipeline:
    
    _MIGRATION_VERSIONS: List[_LegacyData] = [
        _LegacyData(
            version="0.9.0-beta",
            migration_method="_migrate_v090_to_v0100",
            roaming_dir="Bloodline",
            roaming_src="0.9.0-beta",
            docs_dir="Bloodline",
            alt_signature=["ui_config.json", "save_file.sqlite"]
        )
    ]
    
    
    @classmethod
    def run_all_migrations(cls) -> None:
        pending_migrations: List[_LegacyData] = cls._get_pending_migrations()
        
        if not pending_migrations:
            return
        
        any_roaming_backup: bool = any(migration.roaming_backup_required() for migration in pending_migrations)
        any_docs_backup: bool = any(migration.docs_backup_required() for migration in pending_migrations)
        
        cls._archive_legacy_backup(
            legacy_data=pending_migrations[0],
            roaming_backup_required=any_roaming_backup,
            docs_backup_required=any_docs_backup
        )
        
        for legacy_data in pending_migrations:
            method_name: str = legacy_data.get_migration_method()
            getattr(cls, method_name)(legacy_data)
        
        for legacy_data in pending_migrations:
            cls._cleanup_legacy_data(legacy_data)
    
    
    @staticmethod
    def _archive_legacy_backup(legacy_data: _LegacyData, roaming_backup_required: bool, docs_backup_required: bool) -> None:
        archive_name: str = legacy_data.get_version()
        backup_targets: List[Tuple[Path, Path]] = []
        
        if roaming_backup_required:
            Directory.create_roaming_archive_dir()
            backup_targets.append((
                legacy_data.get_roaming_src_path(),
                Directory.get_roaming_archive_path()
            ))
        
        if docs_backup_required:
            Directory.create_docs_archive_dir()
            backup_targets.append((
                legacy_data.get_docs_src_path(),
                Directory.get_docs_archive_path()
            ))
        
        for src_path, dst_path in backup_targets:
            complete_dst_path: Path = dst_path / archive_name
            
            make_archive(
                root_dir=str(src_path),
                base_name=str(complete_dst_path),
                format="zip"
            )
    
    
    # version specific method below
    
    @classmethod
    def _migrate_v090_to_v0100(cls, legacy_data: _LegacyData) -> None:
        # Roaming migration
        src_path: Path = legacy_data.get_roaming_src_path()
        dst_path: Path = Directory.get_roaming_data_path()
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
        
        entries_to_delete: List[Path] = [
            dst_path / "ui_config.json",
            backup_path / "ui_config.json.bak"
        ]
        cls._delete_entries(entries_to_delete)
        
        # User documents
        docs_src_path: Path = legacy_data.get_docs_path()
        docs_dst_path: Path = Directory.get_docs_data_path()
        
        cls._move_all_data(docs_src_path, docs_dst_path)
    
    
    # helper methods below
    
    @classmethod
    def _get_pending_migrations(cls) -> List[_LegacyData]:
        pending_migrations: List[_LegacyData] = []
        
        for legacy_data in cls._MIGRATION_VERSIONS:
            roaming_src_path: Path = legacy_data.get_roaming_src_path()
            
            if not roaming_src_path.exists():
                continue
            
            if cls._contains_signature_files(legacy_data, roaming_src_path):
                pending_migrations.append(legacy_data)
        return pending_migrations
    
    
    @staticmethod
    def _contains_signature_files(legacy_data: _LegacyData, roaming_src_path: Path) -> bool:
        has_metadata: bool = True if legacy_data.get_metadata() is not None else False
        
        if has_metadata:
            # read and compare json
            return True
        
        return all((roaming_src_path / file).exists() for file in legacy_data.get_alt_signature())
    
    
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
    def _delete_entries(entries: List[Path]) -> None:
        for item in entries:
            if item.is_dir():
                rmtree(str(item))
            else:
                item.unlink()
    
    
    @staticmethod
    def _cleanup_legacy_data(legacy_data: _LegacyData) -> None:
        roaming_path: Path = legacy_data.get_roaming_path()
        docs_path: Path = legacy_data.get_docs_path()
        
        if roaming_path.resolve() != Directory.get_roaming_data_path():
            rmtree(str(roaming_path))
        
        if docs_path.resolve() != Directory.get_docs_data_path():
            rmtree(str(docs_path))