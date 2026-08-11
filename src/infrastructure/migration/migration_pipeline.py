from logging import Logger, getLogger
from pathlib import Path
from shutil import make_archive, copytree, rmtree
from typing import List, Tuple

from platformdirs import user_config_dir, user_data_dir, user_state_dir, user_documents_dir

from .legacy_data import LegacyData
from .version_changes import VersionChanges
from file_io.json import SystemJsonHandler, MigrationJsonHandler
from infrastructure import MessageHub
from infrastructure.config import Directory, MetadataSchema, Metadata, SystemFiles
from schemas.definitions import MetadataModel

class MigrationPipeline:
    
    _msg_provider: MessageHub = MessageHub()
    _logger: Logger = getLogger(__name__)
    
    _MIGRATIONS: List[LegacyData] = [
        LegacyData(
            version="0.9.0-beta",
            schema_version=0,
            migration_method=VersionChanges.migrate_v090_to_091,
            roaming_dirs="Bloodline/0.9.0-beta",
            docs_dirs="Bloodline",
            backup_docs=True,
            alt_signature=["ui_config.json", "save_file.sqlite"]
        ),
        # LegacyData(
        #   ... 
        # ),
        
        # current version
        LegacyData(
            version=Metadata.VERSION,
            schema_version=MetadataSchema.SCHEMA_VERSION.default,
            migration_method=lambda: (),
            roaming_dirs=Directory.ROAMING_DATA_PATH.relative_to(Path(user_config_dir(roaming=True))),
            local_dirs=Directory.LOCAL_DATA_PATH.relative_to(Path(user_data_dir(roaming=False))),
            state_dirs=Directory.STATE_DATA_PATH.relative_to(Path(user_state_dir())) if Metadata.OS_IS_LINUX else None,
            docs_dirs=Directory.DOCS_DATA_PATH.relative_to(Path(user_documents_dir())),
            backup_roaming=False,
            backup_local=False,
            backup_state=False,
            backup_docs=False,
            metadata=SystemFiles.BLOODLINE_METADATA.file_name
        )
    ]
    
    
    @staticmethod
    def setup_meta_files() -> None:
        """
        Handler are only generated to ensure file existence and validation
        """
        file_paths: List[Path] = [
            SystemFiles.BLOODLINE_METADATA.main_file_path,
            SystemFiles.BLOODLINE_METADATA.local_file_path,
            SystemFiles.BLOODLINE_METADATA.docs_file_path
        ]
        
        if Metadata.OS_IS_LINUX:
            file_paths.append(SystemFiles.BLOODLINE_METADATA.state_file_path)
        
        for path in file_paths:
            SystemJsonHandler(
                main_file_path=path,
                validation_model=MetadataModel()
            )
    
    
    @classmethod
    def handle_migration_process(cls) -> None:
        result: Tuple[int, LegacyData] | None = cls._get_first_pending()
        
        if result is None:
            return
        
        start, first_pending = result
        remaining_pending: List[LegacyData] = cls._MIGRATIONS[start:]
        
        cls._archive_legacy_backup(first_pending, remaining_pending)
        
        for index, legacy_data in enumerate(remaining_pending[:-1]):
            try:
                next_legacy_data: LegacyData = remaining_pending[index + 1]
                cls._logger.info(f"Migration started: v{legacy_data.version} -> v{next_legacy_data.version}")
                
                legacy_data.migration_method(legacy_data, next_legacy_data)
                cls._update_schema_version(next_legacy_data)
                cls._logger.info("Migration successful")
            except Exception as e:
                cls._msg_provider.invoke(
                    f"An unexpected error occured while migrating the data to version \"{legacy_data.version}\".\n"
                    f"Exception: {e}", "error"
                )
                return cls._logger.exception("Migration failed")
    
    
    # helper methods below
    
    @classmethod
    def _get_first_pending(cls) -> Tuple[int, LegacyData] | None:
        if cls._check_early_exit():
            return None
        
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
        
        cls._update_schema_version(cls._MIGRATIONS[-1])
        return None
    
    
    @classmethod
    def _check_early_exit(cls) -> bool:
        curr_data: LegacyData = cls._MIGRATIONS[-1]
        
        metadata_file: Path = curr_data.roaming_data_path / curr_data.metadata
        if not metadata_file.exists():
            return False
        
        raw_data: dict | None = MigrationJsonHandler.load_raw(metadata_file)
        if raw_data is None:
            return False
        
        correct_dir: bool = raw_data.get(MetadataSchema.SIGNATURE.alias) == Metadata.URL_REPO
        up_to_date: bool = raw_data.get(MetadataSchema.SCHEMA_VERSION.alias) == MetadataSchema.SCHEMA_VERSION.default
        
        return correct_dir and up_to_date
    
    
    @classmethod
    def _archive_legacy_backup(cls, first_pending: LegacyData, remaining_pending: List[LegacyData]) -> None:
        src_paths: List[Tuple[Path, str]] = []
        
        if any(migration.backup_roaming for migration in remaining_pending):
            src_paths.append((first_pending.roaming_data_path, "roaming"))
        if any(migration.backup_local for migration in remaining_pending) and first_pending.local_data_path is not None:
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
    def _update_schema_version(cls, next_legacy_data: LegacyData) -> None:
        if next_legacy_data.metadata is None:
            return
        
        data_paths: List[Path] = [
            next_legacy_data.roaming_data_path,
            next_legacy_data.docs_data_path
        ]
        
        if next_legacy_data.local_data_path is not None:
            data_paths.append(next_legacy_data.local_data_path)
        
        if next_legacy_data.state_data_path is not None:
            data_paths.append(next_legacy_data.state_data_path)
        
        for path in data_paths:
            meta_handler: SystemJsonHandler = SystemJsonHandler(
                main_file_path=path / next_legacy_data.metadata,
                validation_model=MetadataModel()
            )
            
            data: dict = meta_handler.data
            data[MetadataSchema.SCHEMA_VERSION.alias] = next_legacy_data.schema_version
            
            meta_handler.set_data(data)