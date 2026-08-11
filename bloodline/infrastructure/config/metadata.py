from datetime import datetime
from platform import system

from .field_definition import FieldDef

class Metadata:
    # both vars needed for explicit checks
    _OS_IS_WINDOWS: bool = system() == "Windows"
    OS_IS_LINUX: bool = system() == "Linux"
    
    APP_NAME: str = "Bloodline"
    AUTHOR: str = "NME"
    VERSION: str = "1.0.0"
    
    DIR_APP_NAME: str = APP_NAME if _OS_IS_WINDOWS else APP_NAME.lower()
    DIR_AUTHOR: str = AUTHOR if _OS_IS_WINDOWS else AUTHOR.lower()
    
    _GITHUB_USER: str = "prjbl"
    _REPO_NAME: str = "bloodline"
    URL_REPO: str = f"https://github.com/{_GITHUB_USER}/{_REPO_NAME}"
    URL_LATEST_RELEASE: str = f"https://github.com/{_GITHUB_USER}/{_REPO_NAME}/releases/latest"
    URL_API: str = f"https://api.github.com/repos/{_GITHUB_USER}/{_REPO_NAME}/releases/latest"
    
    UPDATE_TIME_FORMAT: str = "%Y-%m-%d %H:%M"
    UPDATE_INTERVAL_MINUTES: float = 60.0
    UPDATE_TIMEOUT_SECONDS: int = 5
    LAST_API_REQUEST: str = "last_api_request"
    
    DB_SCHEMA_VERSION: int = 1


class MetadataSchema:
    SIGNATURE: FieldDef = FieldDef("signature", Metadata.URL_REPO)
    SCHEMA_VERSION: FieldDef = FieldDef("schema_version", 1)
    
    LAST_API_REQUEST: FieldDef = FieldDef(Metadata.LAST_API_REQUEST, lambda: datetime.now().strftime(Metadata.UPDATE_TIME_FORMAT))