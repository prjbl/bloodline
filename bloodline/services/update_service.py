from datetime import datetime, timedelta
from itertools import zip_longest
from json import JSONDecodeError
from re import findall
from typing import Any, List

from requests import get, Response, RequestException

from .web_manager import WebManager
from file_io.json import SystemJsonHandler
from infrastructure import MessageHub
from infrastructure.config import Metadata, SystemFiles
from schemas.definitions import UpdateModel

class UpdateService:
    
    def __init__(self):
        self._update_file_exists: bool = SystemFiles.UPDATE_STATE.main_file_path.exists() or SystemFiles.UPDATE_STATE.backup_file_path.exists()
        self._msg_provider: MessageHub = MessageHub()
        
        self._sys_json_handler: SystemJsonHandler = SystemJsonHandler(
            main_file_path=SystemFiles.UPDATE_STATE.main_file_path,
            validation_model=UpdateModel()
        )
    
    
    def check_for_update(self) -> None:
        if not self._get_check_allowed():
            return
        
        try:
            response: Response = get(
                url=Metadata.URL_API,
                headers=WebManager.GITHUB_HEADERS,
                timeout=Metadata.UPDATE_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            
            data: dict = response.json()
            latest_version: str = data["tag_name"]
            
            if self._get_new_version_available(latest_version):
                release_url: str = Metadata.URL_LATEST_RELEASE
                self._msg_provider.invoke(f"A newer version \"{latest_version}\" is available to download at:", "note")
                self._msg_provider.invoke(release_url, "hyperlink", release_url)
        except JSONDecodeError:
            self._msg_provider.invoke("The fetched update data is corrupted or invalid. The update check is being aborted", "error")
        except RequestException:
            pass
    
    
    # helper methods below
    
    def _get_check_allowed(self) -> bool:
        current_timestamp: datetime = datetime.now()
        update_state: dict = self._sys_json_handler.data
        last_api_request: datetime = datetime.strptime(update_state[Metadata.LAST_API_REQUEST], Metadata.UPDATE_TIME_FORMAT)
        
        if not self._update_file_exists:
            return True
        
        if current_timestamp < last_api_request + timedelta(minutes=Metadata.UPDATE_INTERVAL_MINUTES):
            return False
        
        update_state[Metadata.LAST_API_REQUEST] = current_timestamp.strftime(Metadata.UPDATE_TIME_FORMAT)
        self._sys_json_handler.set_data(update_state)
        return True
    
    
    def _get_new_version_available(self, latest_version: str) -> bool:
        curr_version: str = Metadata.VERSION
        parsed_curr_version: List[int] = self._parse_version(curr_version)
        parsed_latest_version: List[int] = self._parse_version(latest_version)
        
        for curr, latest in zip_longest(parsed_curr_version, parsed_latest_version, fillvalue=0):
            if curr > latest:
                return False
            if latest > curr:
                return True
        return False
    
    
    @staticmethod
    def _parse_version(version: str) -> List[int]:
        numbers: List[Any] = findall(r"\d+", version)
        return [int(x) for x in numbers]