from datetime import datetime, timedelta
from itertools import zip_longest
from json import JSONDecodeError
from pathlib import Path
from re import findall
from typing import Any, List

from requests import get, Response, RequestException

from .web_manager import WebManager
from file_io.json import PersistentJsonHandler
from infrastructure import Directory, MessageHub
from schemas import UpdateModel, UpdateKeys, RequestTime

class UpdateService:
    
    def __init__(self, request_interval_minutes: float):
        self._request_interval_minutes: float = request_interval_minutes
        
        self._update_file_exists: bool = UpdateService._UPDATE_FILE_PATH.exists() or UpdateService._BACKUP_FILE_PATH.exists()
        self._msg_provider: MessageHub = MessageHub()
        
        self._pers_json_handler: PersistentJsonHandler = PersistentJsonHandler(
            main_file_path=UpdateService._UPDATE_FILE_PATH,
            backup_file_path=UpdateService._BACKUP_FILE_PATH,
            default_data=UpdateModel()
        )
        self._pers_json_handler.load_data()
    
    
    _UPDATE_FILE: str = "update_state.json"
    _BACKUP_FILE: str = f"{_UPDATE_FILE}.bak"
    _UPDATE_FILE_PATH: Path = Directory.get_persistent_data_path() / _UPDATE_FILE
    _BACKUP_FILE_PATH: Path = Directory.get_backup_path() / _BACKUP_FILE
    
    
    def check_for_update(self) -> None:
        if not self._get_check_allowed():
            return
        
        try:
            response: Response = get(
                url=WebManager.get_api_url(),
                headers=WebManager.get_headers(),
                timeout=5
            )
            response.raise_for_status()
            
            data: dict = response.json()
            latest_version: str = data.get("tag_name")
            
            if self._get_new_version_available(latest_version):
                release_url: str = WebManager.get_release_url()
                self._msg_provider.invoke(f"A newer version \"{latest_version}\" is available to download at:", "note")
                self._msg_provider.invoke(release_url, "hyperlink", release_url)
        except JSONDecodeError:
            self._msg_provider.invoke("The fetched update data is corrupted or invalid. The update check is being aborted", "error")
        except RequestException:
            pass
    
    
    # helper methods below
    
    def _get_check_allowed(self) -> bool:
        current_timestamp: datetime = datetime.now()
        update_state: dict = self._pers_json_handler.get_data()
        last_api_request: datetime = datetime.strptime(update_state.get(UpdateKeys.LAST_API_REQUEST), RequestTime.TIME_FORMAT)
        
        if not self._update_file_exists:
            return True
        
        if current_timestamp < last_api_request + timedelta(minutes=self._request_interval_minutes):
            return False
        
        update_state[UpdateKeys.LAST_API_REQUEST] = current_timestamp.strftime(RequestTime.TIME_FORMAT)
        self._pers_json_handler.set_data(update_state)
        return True
    
    
    def _get_new_version_available(self, latest_version: str) -> bool:
        curr_version: str = Directory.get_version()
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