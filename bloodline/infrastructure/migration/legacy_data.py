from pathlib import Path
from typing import List, Callable

from platformdirs import user_data_dir, user_documents_dir

class LegacyData:
    
    def __init__(
        self,
        version: str,
        migration_method: Callable[..., None],
        roaming_root: str,
        docs_root: str,
        roaming_src: str | None = None,
        docs_src: str | None = None,
        roaming_backup: bool = True,
        docs_backup: bool = True,
        metadata: str | None = None,
        alt_signature: List[str] | None = None
    ):
        self._version: str = version
        self._migration_method: Callable[..., None] = migration_method
        self._roaming_path: Path = Path(user_data_dir(roaming=True)) / roaming_root
        self._docs_path: Path = Path(user_documents_dir()) / docs_root
        self._roaming_src_path: Path = self._roaming_path / roaming_src if roaming_src is not None else self._roaming_path
        self._docs_src_path: Path = self._docs_path / docs_src if docs_src is not None else self._docs_path
        self._roaming_backup: bool = roaming_backup
        self._docs_backup: bool = docs_backup
        self._metadata: str | None = metadata
        self._alt_signature: List[str] | None = alt_signature
    
    
    def get_version(self) -> str:
        return self._version
    
    
    def get_migration_method(self) -> Callable[..., None]:
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