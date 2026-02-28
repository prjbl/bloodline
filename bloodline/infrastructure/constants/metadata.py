from datetime import datetime

from .base_constant import Const

class Metadata:
    APP_NAME: str = "Bloodline"
    AUTHOR: str = "Project Bloodline"
    VERSION: str = "0.9.1-beta"
    
    _GITHUB_USER: str = "prjbl"
    _REPO_NAME: str = "bloodline"
    URL_REPO: str = f"https://github.com/{_GITHUB_USER}/{_REPO_NAME}"
    URL_LATEST_RELEASE: str = f"https://github.com/{_GITHUB_USER}/{_REPO_NAME}/releases/latest"
    URL_API: str = f"https://api.github.com/repos/{_GITHUB_USER}/{_REPO_NAME}/releases/latest"
    
    UPDATE_TIME_FORMAT: str = "%Y-%m-%d %H:%M"
    UPDATE_INTERVAL_MINUTES: float = 60.0
    UPDATE_TIMEOUT_SECONDS: int = 5
    LAST_API_REQUEST: str = "last_api_request"


class MetadataSchema:
    VERSION: Const = Const("version", Metadata.VERSION)
    SIGNATURE: Const = Const("signature", Metadata.URL_REPO)
    SCHEMA_VERSION: Const = Const("schema_version", 1)
    
    LAST_API_REQUEST: Const = Const(Metadata.LAST_API_REQUEST, lambda: datetime.now().strftime(Metadata.UPDATE_TIME_FORMAT))