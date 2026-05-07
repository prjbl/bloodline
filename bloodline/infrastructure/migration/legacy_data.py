from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

from platformdirs import user_data_dir, user_documents_dir

@dataclass(frozen=True)
class LegacyData:
    version: str
    schema_version: int
    migration_method: Callable[..., None]
    roaming_dirs: str
    docs_dirs: str
    local_dirs: str | None = None
    backup_roaming: bool = True
    backup_docs: bool = False
    backup_local: bool = False
    metadata: str | None = None
    alt_signature: List[str] | None = None
    
    def __post_init__(self):
        if self.metadata is None and self.alt_signature is None:
            raise ValueError("At least one of the signature options must be provided.")
    
    
    @property
    def roaming_data_path(self) -> Path:
        return Path(user_data_dir(roaming=True)) / self.roaming_dirs
    
    
    @property
    def local_data_path(self) -> Path | None:
        return Path(user_data_dir(roaming=False)) / self.local_dirs if self.local_dirs is not None else None
    
    
    @property
    def docs_data_path(self) -> Path:
        return Path(user_documents_dir()) / self.docs_dirs