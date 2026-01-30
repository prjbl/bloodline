from pathlib import Path
from shutil import copy2
from sqlite3 import Connection, Cursor, connect, DatabaseError
from typing import Any, Callable, List

from infrastructure import MessageHub

class DatabaseHandler:
    
    def __init__(self, db_file_path: Path, backup_file_path: Path, latest_version: int, db_structure: str, db_updates: Callable):
        self._db_file_path: Path = db_file_path
        self._backup_file_path: Path = backup_file_path
        self._latest_version: int = latest_version
        self._db_structure: str = db_structure
        self._db_updates: Callable = db_updates
        
        self._db_file_name: str = db_file_path.name
        self._backup_file_name: str = backup_file_path.name
        
        self._msg_provider: MessageHub = MessageHub()
        self._conn: Connection | None = None
        self._cursor: Cursor | None = None
        
        self._setup_files()
    
    
    def _setup_files(self) -> None:
        db_file_exists: bool = self._db_file_path.exists()
        backup_file_exists: bool = self._backup_file_path.exists()
        
        if not db_file_exists and not backup_file_exists:
            self._open_connection()
            self._setup_db()
            self.ensure_backup()
            return
        
        if not db_file_exists:
            self._handle_file_restore()
        else:
            self._open_connection()
            self._setup_db() # handles file restore if db file exists but is corrupted
        
        if not backup_file_exists:
            self.ensure_backup()
        
        self._check_for_updates()
    
    
    def execute_dml(self, sql: str, *params: Any) -> None:
        self._cursor.execute(sql, params)
        self._conn.commit()
    
    
    def fetch(self, sql: str, *params: Any) -> List[tuple]:
        self._cursor.execute(sql, params)
        return self._cursor.fetchall()
    
    
    def get_table_description(self) -> tuple:
        return self._cursor.description
    
    
    def ensure_backup(self) -> None:
        try:
            self._handle_backup_process()
        except DatabaseError:
            self._msg_provider.invoke(f"The file \"{self._backup_file_name}\" is corrupted. It will be re-initialized", "error")
            self._reinitialize_backup_file()
    
    
    def close_connection(self) -> None:
        if self._conn:
            self._conn.close()
        self._conn = None
        self._cursor = None
    
    
    # helper methods below
    
    def _open_connection(self) -> None:
        self._conn = connect(self._db_file_path)
        self._conn.execute("PRAGMA foreign_keys = ON") # activates foreign key restriction
        self._cursor = self._conn.cursor()
    
    
    def _setup_db(self) -> None:
        try:
            self._create_tables()
        except DatabaseError:
            self._msg_provider.invoke(f"The file \"{self._db_file_name}\" is corrupted. An attempt is made to load the last backup", "error")
            self._handle_file_restore()
    
    
    def _create_tables(self) -> None:
        self._cursor.executescript(self._db_structure)
        self._conn.commit()
    
    
    def _check_for_updates(self) -> None:
        self._cursor.execute("PRAGMA user_version")
        curr_version: int = self._cursor.fetchone()[0]
        
        if not curr_version:
            self._cursor.execute(f"PRAGMA user_version = {self._latest_version}")
            self._conn.commit()
            return
        
        if curr_version == self._latest_version:
            return
        
        self._db_updates(curr_version)
    
    
    def _handle_file_restore(self) -> None:
        if not self._backup_file_path.exists():
            self._msg_provider.invoke("No save file backup could be found. Both files will be re-initialized", "error")
            self._reinitialize_db_file()
            self._reinitialize_backup_file()
            return
        
        try:
            self._backup_integrity_check() # checks if backup file is corrupted
            
            if self._conn:
                self.close_connection()
            
            self._db_file_path.unlink(missing_ok=True)
            self._load_backup()
            self._open_connection()
            self._msg_provider.invoke(f"Loading the backup from \"{self._backup_file_name}\" was successful", "success")
        except DatabaseError:
            self._msg_provider.invoke(f"The file \"{self._backup_file_name}\" is corrupted. Both files will be re-initialized", "error")
            self._reinitialize_db_file()
            self._reinitialize_backup_file()
            
            if not self._conn:
                self._open_connection()
    
    
    def _handle_backup_process(self) -> None:
        if not self._conn:
            self._open_connection()
        
        backup_conn: Connection | None = None
        
        try:
            backup_conn = connect(self._backup_file_path)
            self._conn.backup(backup_conn)
        finally:
            if backup_conn:
                backup_conn.close()
    
    
    def _backup_integrity_check(self) -> None:
        backup_conn: Connection | None = None
        
        try:
            backup_conn = connect(self._backup_file_path)
            result: Any = backup_conn.cursor().execute("PRAGMA integrity_check").fetchone()[0]
            
            if result != "ok":
                raise DatabaseError
        finally:
            backup_conn.close()
    
    
    def _load_backup(self) -> None:
        copy2(self._backup_file_path, self._db_file_path)
    
    
    def _reinitialize_db_file(self) -> None:
        try:
            self.close_connection()
            self._db_file_path.unlink(missing_ok=True)
            self._open_connection()
            self._create_tables()
            self._msg_provider.invoke(f"The file \"{self._db_file_name}\" was re-initialized successfully", "success")
        except Exception as e:
            self._msg_provider.invoke(
                f"An unexpected error occurred while re-initializing the file \"{self._db_file_name}\".\n"
                f"Exception: {e}", "error"
            )
    
    
    def _reinitialize_backup_file(self) -> None:
        try:
            self._backup_file_path.unlink(missing_ok=True)
            self._handle_backup_process()
            self._msg_provider.invoke(f"The file \"{self._backup_file_name}\" was re-initialized successfully", "success")
        except Exception as e:
            self._msg_provider.invoke(
                f"An unexpected error occurred while re-initializing the file \"{self._backup_file_name}\".\n"
                f"Exception: {e}", "error"
            )