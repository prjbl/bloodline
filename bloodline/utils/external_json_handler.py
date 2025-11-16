from json import JSONDecodeError
from pathlib import Path

from .json_file_operations import JsonFileOperations

class ExternalJsonHandler(JsonFileOperations):
    
    def load_data(self, src_file_path: Path) -> dict:
        data: dict = {}
        
        try:
            data = super().perform_load(src_file_path)
            data = self._validate_file_structure(data)
        except JSONDecodeError:
            # put message in queue
            pass
        finally:
            return data
    
    
    # helper methods below
    
    """def _validate_file_structure(self, loaded_data: dict) -> dict:
        keys_to_ignore: set = set()
        
        for key, value in loaded_data.items():
            if not isinstance(value, list):
                keys_to_ignore.add(key)
                # put message in queue
                continue
            
            self._validate_value_type(value)
            
            if not value: # check after value type validation to delete all empty lists
                keys_to_ignore.add(key)
                # put message in queue
        
        for key in keys_to_ignore:
            del loaded_data[key]
        
        return loaded_data
    
    
    def _validate_value_type(self, value: list) -> None:
        indices_to_ignore: list[int] = []
        
        for index, item in enumerate(value):
            if not isinstance(item, str):
                indices_to_ignore.append(index)
                # put message in queue
        
        for index in sorted(indices_to_ignore, reverse=True): # has to be reversed to prevent all elements to delete from moving while iterating
            del value[index]"""
    
    
    """def _validate_value_type(self, value: list) -> list[str]: # list comprehension alternative
        indices_to_ignore: list[str] = [
            item for item in value
            if isinstance(item, str)
        ]
        return indices_to_ignore"""