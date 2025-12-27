from pathlib import Path
from re import compile, fullmatch, Match, IGNORECASE
from typing import List

from .json import JsonFileOperations
from interfaces import IInterceptCommand

class CommandOperations:
    
    @staticmethod
    def get_input_pattern_result(instance: IInterceptCommand, pattern_type: str, console_input: str) -> List[str]:
        valid_input_pattern: str = ""
        
        if pattern_type == "single":
            valid_input_pattern = compile(r"\"([^\"]+)\"$")
        elif pattern_type == "double":
            valid_input_pattern = compile(r"\"([^\"]+)\", \"([^\"]+)\"$")
        elif pattern_type == "single_single":
            valid_input_pattern = compile(r"\"([^\"]+)\" -> \"([^\"]+)\"$")
        elif pattern_type == "single_double":
            valid_input_pattern = compile(r"\"([^\"]+)\" -> \"([^\"]+)\", \"([^\"]+)\"$")
        elif pattern_type == "double_single":
            valid_input_pattern = compile(r"\"([^\"]+)\", \"([^\"]+)\" -> \"([^\"]+)\"$")
        elif pattern_type == "yes_no":
            valid_input_pattern = compile(r"((?:y(?:es)?)|(?:n(?:o)?))", IGNORECASE) # ?: ignores group so only one group is returning
        
        result: Match | None = fullmatch(valid_input_pattern, console_input)
        
        if result is None:
            instance.print_invalid_input_pattern("The input does not match the pattern. Please try again", "invalid")
            return []
        return list(map(str, result.groups()))
    
    
    @staticmethod
    def check_external_file_props(instance: IInterceptCommand, src_file_path: Path) -> bool:
        if not src_file_path.exists():
            instance.print_invalid_input_pattern(f"The path '{src_file_path}' does not exists. Process is beeing canceled", "invalid")
            return False
        elif not JsonFileOperations.check_json_extension(src_file_path):
            instance.print_invalid_input_pattern(f"The file '{src_file_path}' is not a .json file. Process is beeing canceled", "invalid")
            return False
        return True