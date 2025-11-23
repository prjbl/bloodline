from csv import writer
from pathlib import Path
from typing import Any

class CsvFileOperations:
    
    @staticmethod
    def perform_save(dst_file_path: Path, headers: list[str], data: list[tuple]) -> None:
        with open(dst_file_path, "w", newline="", encoding="utf-8") as output:
            csv_writer: Any = writer(output, delimiter=";") # the actual type hint is an internal var of the csv module
            csv_writer.writerow(header.upper() for header in headers)
            csv_writer.writerows(data)