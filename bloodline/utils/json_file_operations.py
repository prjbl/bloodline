from json import load, dump
from pathlib import Path

class JsonFileOperations:
    
    @staticmethod
    def check_json_extension(src_file_path: Path) -> bool:
        if src_file_path.suffix == ".json":
            return True
        return False
    
    
    @staticmethod
    def perform_load(src_file_path: Path) -> dict:
        with open(src_file_path, "r") as input:
            return load(input)
    
    
    @staticmethod
    def perform_save(dst_file_path: Path, data: dict) -> None:
        with open(dst_file_path, "w") as output:
            dump(data, output, indent=4)