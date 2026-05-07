from pathlib import Path
from shutil import make_archive, copytree, rmtree
from typing import List, Tuple

from .legacy_data import LegacyData
from file_io.json import SystemJsonHandler, MigrationJsonHandler
from infrastructure import MessageHub
from infrastructure.config import Directory, MetadataSchema, Metadata, SystemFiles
from schemas.definitions import MetadataModel

class MigrationPipeline:
    
    _msg_provider: MessageHub = MessageHub()
    
    _roaming_meta_handler: SystemJsonHandler = SystemJsonHandler(
        main_file_path=SystemFiles.BLOODLINE_METADATA.main_file_path,
        validation_model=MetadataModel()
    )
    _local_meta_handler: SystemJsonHandler = SystemJsonHandler(
        main_file_path=SystemFiles.BLOODLINE_METADATA.local_file_path,
        validation_model=MetadataModel()
    )
    _docs_meta_handler: SystemJsonHandler = SystemJsonHandler(
        main_file_path=SystemFiles.BLOODLINE_METADATA.docs_file_path,
        validation_model=MetadataModel()
    )
    
    _MIGRATIONS: List[LegacyData] = [
        LegacyData(
            version="0.9.0-beta",
            schema_version=0,
            migration_method=lambda: (),
            roaming_dirs="Bloodline/0.9.0-beta",
            docs_dirs="Bloodline",
            backup_docs=True,
            alt_signature=["ui_config.json", "save_file.sqlite"]
        ),
        LegacyData(
            version="0.9.1-testversion",
            schema_version=1,
            migration_method=lambda: (),
            roaming_dirs="NME/Bloodline",
            local_dirs="NME/Bloodline",
            docs_dirs="NME/Bloodline",
            metadata=".bloodline.metadata"
        )
    ]
    
    
    @classmethod
    def handle_migration_process(cls) -> None:
        result: Tuple[int, LegacyData] | None = cls._get_first_pending()
        
        if result is None:
            return
        
        start, first_pending = result
        remaining_pending: List[LegacyData] = cls._MIGRATIONS[start:]
        
        cls._archive_legacy_backup(first_pending, remaining_pending)
        
        for legacy_data in remaining_pending:
            try:
                legacy_data.migration_method(legacy_data)
                cls._update_schema_version(legacy_data)
            except Exception as e:
                return cls._msg_provider.invoke(
                    f"An unexpected error occured while migrating the data to version \"{legacy_data.version}\".\n"
                    f"Exception: {e}", "error"
                )
    
    
    # helper methods below
    
    @classmethod
    def _get_first_pending(cls) -> Tuple[int, LegacyData] | None:
        for index, legacy_data in enumerate(cls._MIGRATIONS):
            roaming_data_path: Path = legacy_data.roaming_data_path
            
            if not roaming_data_path.exists():
                continue
            
            if legacy_data.alt_signature is not None:
                if all((roaming_data_path / file).exists() for file in legacy_data.alt_signature):
                    return index, legacy_data
                continue
            
            metadata_file: Path = roaming_data_path / legacy_data.metadata
            if not metadata_file.exists():
                continue
            
            raw_data: dict | None = MigrationJsonHandler.load_raw(metadata_file)
            if raw_data is None:
                continue
            
            correct_dir: bool = raw_data.get(MetadataSchema.SIGNATURE.alias) == Metadata.URL_REPO
            migration_required: bool = raw_data.get(MetadataSchema.SCHEMA_VERSION.alias) < MetadataSchema.SCHEMA_VERSION.default
            
            if correct_dir and migration_required:
                return index, legacy_data
        return None
    
    
    @classmethod
    def _archive_legacy_backup(cls, first_pending: LegacyData, remaining_pending: List[LegacyData]) -> None:
        src_paths: List[Tuple[Path, str]] = []
        
        if any(migration.backup_roaming for migration in remaining_pending):
            src_paths.append((first_pending.roaming_data_path, "roaming"))
        if any(migration.backup_local for migration in remaining_pending):
            src_paths.append((first_pending.local_data_path, "appdata_local"))
        if any(migration.backup_docs for migration in remaining_pending):
            src_paths.append((first_pending.docs_data_path, "user_documents"))
        
        if not src_paths:
            return
        
        Directory.create_archive_dir()
        cls._create_archive(src_paths, first_pending.version)
    
    
    @staticmethod
    def _create_archive(src_paths: List[Tuple[Path, str]], archive_name: str) -> None:
        tmp_path: Path = Directory.ARCHIVE_PATH / "_tmp"
        
        try:
            for src_path, subdir in src_paths:
                copytree(src_path, tmp_path / subdir)
            
            make_archive(
                root_dir=tmp_path,
                base_name=Directory.ARCHIVE_PATH / archive_name,
                format="zip"
            )
        finally:
            rmtree(tmp_path, ignore_errors=True)
    
    
    @classmethod
    def _update_schema_version(cls, legacy_data: LegacyData) -> None:
        data: dict = cls._roaming_meta_handler.data
        data[MetadataSchema.VERSION.alias] = legacy_data.version
        data[MetadataSchema.SCHEMA_VERSION.alias] = legacy_data.schema_version
        
        cls._roaming_meta_handler.set_data(data)
        cls._local_meta_handler.set_data(data)
        cls._docs_meta_handler.set_data(data)