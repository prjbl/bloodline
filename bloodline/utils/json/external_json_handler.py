from json import JSONDecodeError
from pathlib import Path
from pydantic import BaseModel, RootModel

from .json_file_operations import JsonFileOperations

class ExternalJsonHandler(JsonFileOperations):
    
    @classmethod
    def load_data(cls, src_file_path: Path, model: BaseModel | RootModel) -> dict:
        data: dict = {}
        try:
            raw_json: dict = super().perform_load(src_file_path)
            data = model.model_validate(raw_json).model_dump()
        except JSONDecodeError:
            # put message in queue
            pass
        finally:
            return data