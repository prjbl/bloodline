from pydantic import RootModel, model_validator
from typing import Any, Dict, List

_PRESET_STRUCTURE = Dict[str, List[str]]

class PresetModel(RootModel[_PRESET_STRUCTURE]):
    
    @model_validator(mode="before")
    @classmethod
    def enforce_correct_data_type(cls, raw_json: Any) -> Any:
        if not isinstance(raw_json, dict):
            return {}
        
        cleaned_data: _PRESET_STRUCTURE = {}
        for game_title, list_of_bosses in raw_json.items():
            if not isinstance(list_of_bosses, list):
                continue
            
            cleaned_list_of_bosses: List[str] = []
            for boss in list_of_bosses:
                if not isinstance(boss, str):
                    continue
                cleaned_list_of_bosses.append(boss)
            
            if cleaned_list_of_bosses:
                cleaned_data[game_title] = cleaned_list_of_bosses
        return cleaned_data