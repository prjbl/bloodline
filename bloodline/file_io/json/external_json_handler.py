from json import JSONDecodeError
from pathlib import Path

from pydantic import BaseModel, RootModel

from .json_file_operations import JsonFileOperations
from infrastructure import MessageHub

class ExternalJsonHandler(JsonFileOperations):
    
    _msg_provider: MessageHub = MessageHub()
    
    @classmethod
    def load_data(cls, src_file_path: Path, model: BaseModel | RootModel) -> dict:
        data: dict = {}
        try:
            raw_json: dict = super()._perform_load(src_file_path)
            data = model.model_validate(raw_json).model_dump()
        except JSONDecodeError:
            cls._msg_provider.invoke(f"The file \"{src_file_path.name}\" is corrupted. Please make sure to check it", "error")
        finally:
            return data
    
    
    @classmethod
    def check_external_file_props(cls, src_file_path: Path) -> bool:
        if not src_file_path.exists():
            cls._msg_provider.invoke(f"The path \"{src_file_path}\" does not exist. Process is beeing canceled", "invalid")
            return False
        elif not super()._check_json_extension(src_file_path):
            cls._msg_provider.invoke(f"The file \"{src_file_path.name}\" is not a .json file. Process is beeing canceled", "invalid")
            return False
        return True