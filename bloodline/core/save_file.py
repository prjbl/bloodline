from pathlib import Path
from shutil import copy2
from sqlite3 import Connection, Cursor, connect, DatabaseError

from utils.directory import Directory

class SaveFile:
    
    def __init__(self):
        self._conn: Connection = None
        self._cursor: Cursor = None
        self._observer: any = None
    
    
    _dir: Directory = Directory()
    
    _DB_FILE: str = "save_file.sqlite"
    _BACKUP_FILE: str = f"{_DB_FILE}.bak"
    _DB_FILE_PATH: Path = _dir.get_persistent_data_path().joinpath(_DB_FILE)
    _BACKUP_FILE_PATH: Path = _dir.get_backup_path().joinpath(_BACKUP_FILE)
    
    _LATEST_VERSION: int = 1
    
    _UNKNOWN_GAME_TITLE: str = "Unknown Game"
    _UNKNOWN_BOSS_NAME: str = "Unknown Boss"
    
    
    def setup_db_and_observer(self, observer: any) -> None:
        self._observer = observer
        
        # setup had to be outsourced to after the observer has been set, as its required for the setup process
        if not self._DB_FILE_PATH.exists() and self._BACKUP_FILE_PATH.exists():
            self._notify_observer(f"The file '{self._DB_FILE}' could not be found. The last backup will be loaded", "error")
            self._handle_file_restore()
        else:
            self._open_connection()
            self._setup_db()
        
        if not self._BACKUP_FILE_PATH.exists():
            self._ensure_backup()
        self._check_for_updates()
    
    
    def _notify_observer(self, text: str, text_type: str) -> None:
        self._observer(text, text_type)
    
    
    def _open_connection(self) -> None:
        self._conn = connect(self._dir.get_persistent_data_path().joinpath(self._DB_FILE))
        self._conn.execute("PRAGMA foreign_keys = ON") # activates foreign key restriction
        self._cursor = self._conn.cursor()
    
    
    def _setup_db(self) -> None:
        try:
            self._create_tables()
        except DatabaseError:
            self._notify_observer(f"The file '{self._DB_FILE}' is corrupted. This save file will be deleted and the last backup file is beeing loaded", "error")
            self._handle_file_restore()
    
    
    def _create_tables(self) -> None:
        self._cursor.executescript("""CREATE TABLE IF NOT EXISTS Game (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            title TEXT UNIQUE NOT NULL
                                        );
                                        
                                        CREATE TABLE IF NOT EXISTS Boss (
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            name TEXT NOT NULL,
                                            deaths INTEGER,
                                            requiredTime INTEGER,
                                            gameId INTEGER NOT NULL,
                                        
                                            UNIQUE (name, gameId),
                                            FOREIGN KEY (gameId) REFERENCES Game (id) ON DELETE CASCADE
                                        )""")
        self._conn.commit()
    
    
    def _handle_file_restore(self) -> None:
        if not self._BACKUP_FILE_PATH.exists():
            self._notify_observer("Backup file could not be found. Both files will be re-initialized", "error")
            self._reinitialize_db()
            self._reinitialize_backup()
            self._notify_observer("Both files were successfully re-initilizied", "success")
            return
        
        try:
            self._backup_integrity_check() # checks if backup file is corrupted as well
            if self._conn:
                self.close_connection()
            self._DB_FILE_PATH.unlink(missing_ok=True)
            self._load_backup()
            self._open_connection()
            self._notify_observer("Loading backup was successful", "success")
            self._notify_observer("Whole backuping process was successful", "success")
        except DatabaseError:
            self._notify_observer(f"The backup file '{self._BACKUP_FILE}' is corrupted. An attempt is made to re-initialize file", "error")
            self._reinitialize_db()
            self._reinitialize_backup()
            self._notify_observer("Both files were re-initialized successfully", "success")
    
    
    def _reinitialize_db(self) -> None:
        try:
            self.close_connection()
            self._DB_FILE_PATH.unlink(missing_ok=True)
            self._open_connection()
            self._create_tables()
            self._notify_observer("Save file was re-initialized successfully", "success")
        except Exception as e:
            self._notify_observer(f"Failed to re-initilize '{self._DB_FILE}'. Exception: {e}", "error")
    
    
    def _reinitialize_backup(self) -> None:
        try:
            self._BACKUP_FILE_PATH.unlink(missing_ok=True)
            self._handle_backup_process()
            self._notify_observer("Backup was re-initialized successfully", "success")
        except Exception as e:
            self._notify_observer(f"Failed to re-initialize '{self._BACKUP_FILE}'. Exception: {e}", "error")
    
    
    def _ensure_backup(self) -> None:
        backup_exists: bool = self._BACKUP_FILE_PATH.exists()
        
        try:
            self._handle_backup_process()
            
            if backup_exists:
                self._notify_observer("Backup was updated", "normal")
        except DatabaseError:
            self._notify_observer(f"The backup file '{self._BACKUP_FILE}' is corrupted. An attempt is made to re-initialize file", "error")
            self._reinitialize_backup()
    
    
    def _handle_backup_process(self) -> None:
        backup_conn: Connection = None
        
        try:
            backup_conn = connect(self._BACKUP_FILE_PATH)
            self._conn.backup(backup_conn)
        finally:
            if backup_conn:
                backup_conn.close()
    
    
    def _load_backup(self) -> None:
        copy2(self._BACKUP_FILE_PATH, self._DB_FILE_PATH)
    
    
    def _backup_integrity_check(self) -> None:
        try:
            backup_conn: Connection = connect(self._BACKUP_FILE_PATH)
            backup_conn.cursor().execute("PRAGMA integrity_check")
        finally:
            backup_conn.close()
    
    
    def _check_for_updates(self) -> None:
        self._cursor.execute("PRAGMA user_version")
        selection: int = self._cursor.fetchone()[0]
        
        if not selection:
            self._cursor.execute(f"PRAGMA user_version = {self._LATEST_VERSION}")
            return
        
        if selection == self._LATEST_VERSION:
            return
        
        """try:
            if selection == 1:
                # update 1
            elif selection == 2:
                # update 2
            etc.
        except ..."""
    
    
    def close_connection(self) -> None:
        self._conn.close()
    
    
    # db manipulation and selection methods below
    
    def _add_game(self, game_title: str) -> None:
        if self._get_specific_game_exists(game_title):
            return
        
        try:
            self._cursor.execute("""INSERT INTO Game (title)
                                        VALUES (?)""", (game_title,))
            self._conn.commit()
            
            self._notify_observer(f"The game '{game_title}' has been added to the save file", "normal")
        except Exception as e:
            self._notify_observer(f"An unexpected error occured while adding the game '{game_title}'. Exception: {e}", "error")
    
    
    def add_boss(self, boss_name: str, game_title: str, ensure_backup: bool = True) -> bool:
        if self.get_specific_boss_exists(boss_name, game_title):
            self._notify_observer(f"The boss '{self._get_specific_boss(boss_name, game_title)}' of game '{self._get_specific_game(game_title)}' already exists in the save file", "invalid")
            return False
        
        self._add_game(game_title)
        
        try:
            self._cursor.execute("""INSERT INTO Boss (name, gameId)
                                        VALUES (?, (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE))""", (boss_name, game_title))
            self._conn.commit()
            
            self._notify_observer(f"The boss '{boss_name}' of game '{self._get_specific_game(game_title) if self._get_specific_game_exists(game_title) else game_title}' has been added to the save file", "normal")
            
            if ensure_backup:
                self._ensure_backup()
            return True
        except Exception as e:
            self._notify_observer(f"An unexpected error occured while adding the boss '{boss_name}' to '{self._get_specific_game(game_title) if self._get_specific_game_exists(game_title) else game_title}'. Exception: {e}", "error")
            return False
    
    
    def add_preset(self, loaded_preset: dict) -> None:
        if not loaded_preset:
            self._notify_observer("The imported preset does not contain any values to be added to the save file", "invalid")
            return
        
        changes_made: bool = False
        for game_title, list_of_bosses in loaded_preset.items():
            for boss_name in list_of_bosses:
                boss_added: bool = self.add_boss(boss_name, game_title, ensure_backup=False)
                changes_made = changes_made or boss_added # if changed_made is True onces, it keeps the True state even if boss_added is False
        
        if changes_made:
            self._ensure_backup()
    
    
    def add_unknown(self) -> None:
        self._cursor.execute(f"""SELECT b.name FROM Boss b
                                    JOIN Game g ON b.gameId = g.id
                                    WHERE b.name LIKE '{self._UNKNOWN_BOSS_NAME}%' and g.title = '{self._UNKNOWN_GAME_TITLE}'""")
        selection: list[tuple] = self._cursor.fetchall()
        
        unknown_boss_nums: list[int] = self._get_unknown_boss_numbers(selection)
        
        boss_name_exists: bool = True
        iterator: int = 0
        
        while boss_name_exists:
            iterator += 1
            
            if not iterator in unknown_boss_nums:
                boss_name_exists = False
                self.add_boss(f"{self._UNKNOWN_BOSS_NAME} {iterator}", self._UNKNOWN_GAME_TITLE)
    
    
    def identify_boss(self, unknown_boss_number: str, new_boss_name: str, new_game_title: str) -> None:
        if not self._get_specific_game_exists(self._UNKNOWN_GAME_TITLE):
            self._notify_observer(f"The game '{self._UNKNOWN_GAME_TITLE}' you want to identify a boss from does not exists in the save file so far", "invalid")
            return
        elif not self.get_specific_boss_exists(f"{self._UNKNOWN_BOSS_NAME} {unknown_boss_number}", self._UNKNOWN_GAME_TITLE):
            self._notify_observer(f"The boss '{self._UNKNOWN_BOSS_NAME} {unknown_boss_number}' you selected to identify does not exists in the game '{self._UNKNOWN_GAME_TITLE}' in the save file", "invalid")
            return
        elif not self._get_specific_game_exists(new_game_title):
            self._notify_observer(f"The game '{new_game_title}' you selected to link the boss to does not exists in the save file so far", "invalid")
            return
        elif self.get_specific_boss_exists(new_boss_name, new_game_title):
            self._notify_observer(f"The boss '{self._get_specific_boss(new_boss_name, new_game_title)}' already exists in the game '{self._get_specific_game(new_game_title)}'", "invalid")
            return
            
        if not self._rename_boss_operation(f"{self._UNKNOWN_BOSS_NAME} {unknown_boss_number}", self._UNKNOWN_GAME_TITLE, new_boss_name):
            return
        
        if not self._move_boss_operation(new_boss_name, self._UNKNOWN_GAME_TITLE, new_game_title):
            return
        
        self._notify_observer(f"The boss '{self._UNKNOWN_BOSS_NAME} {unknown_boss_number}' was identified as '{new_boss_name}' from game '{self._get_specific_game(new_game_title)}'", "success")
        self._ensure_backup()
    
    
    def move_boss(self, boss_name: str, game_title: str, new_game_title: str) -> None:
        if not self._get_specific_game_exists(game_title):
            self._notify_observer(f"The game '{game_title}' you selected to move the boss from does not exists in the save file so far", "indication")
            return
        elif not self.get_specific_boss_exists(boss_name, game_title):
            self._notify_observer(f"The boss '{boss_name}' you selected to move does not exists in the game '{self._get_specific_game(game_title)}' in the save file so far", "indication")
            return
        elif not self._get_specific_game_exists(new_game_title):
            self._notify_observer(f"The game '{new_game_title}' you selected to be moved to does not exists in the save file so far", "indication")
            return
        elif self.get_specific_boss_exists(boss_name, new_game_title):
            self._notify_observer(f"The boss '{self._get_specific_boss(boss_name, game_title)}' already exists in the game '{self._get_specific_game(new_game_title)}'", "indication")
            return
        
        old_game_title: str = self._get_specific_game(game_title)
        
        if self._move_boss_operation(boss_name, game_title, new_game_title):
            self._notify_observer(f"The boss '{self._get_specific_boss(boss_name, new_game_title)}' was moved from game '{old_game_title}' to '{self._get_specific_game(new_game_title)}'", "success")
            self._ensure_backup()
    
    
    def rename_game(self, game_title: str, new_game_title: str) -> None:
        if not self._get_specific_game_exists(game_title):
            self._notify_observer(f"The game '{game_title}' you wish to rename does not exists in the save file so far", "indication")
            return
        elif self._get_specific_game_exists(new_game_title, case_insensitive=False):
            self._notify_observer(f"The game '{new_game_title}' already exists with the same spelling in the save file", "invalid")
            return
        
        try:
            old_game_title: str = self._get_specific_game(game_title)
            
            self._cursor.execute("""UPDATE Game
                                        SET title = (?)
                                        WHERE title = (?) COLLATE NOCASE""", (new_game_title, game_title))
            self._conn.commit()
            
            self._notify_observer(f"The game '{old_game_title}' was renamed to '{new_game_title}'", "success")
            self._ensure_backup()
        except Exception as e:
            self._notify_observer(f"An unexpected error occured while renaming the game '{self._get_specific_game(game_title)}' to '{new_game_title}'. Exception: {e}", "error")
    
    
    def rename_boss(self, boss_name: str, game_title: str, new_boss_name: str) -> None:
        if not self._get_specific_game_exists(game_title):
            self._notify_observer(f"The game '{game_title}' you selected does not exists in the save file", "indication")
            return
        elif not self.get_specific_boss_exists(boss_name, game_title):
            self._notify_observer(f"The boss '{boss_name}' you wish to rename does not exists in in the game '{self._get_specific_game(game_title)}' in the save file so far", "indication")
            return
        elif self.get_specific_boss_exists(new_boss_name, game_title, case_insensitive=False):
            self._notify_observer(f"The boss '{new_boss_name}' already exists with the same spelling in the game '{self._get_specific_game(game_title)}'", "invalid")
            return
        
        old_boss_name: str = self._get_specific_boss(boss_name, game_title)
        
        if self._rename_boss_operation(boss_name, game_title, new_boss_name):
            self._notify_observer(f"The boss '{old_boss_name}' of game '{self._get_specific_game(game_title)}' was renamed to '{new_boss_name}'", "success")
            self._ensure_backup()
    
    
    def delete_game(self, game_title: str) -> None:
        if not self._get_specific_game_exists(game_title):
            self._notify_observer(f"The game '{game_title}' you wish to delete does not exists in the save file", "indication")
            return
        
        try:
            removed_game: str = self._get_specific_game(game_title)
            
            self._cursor.execute("""DELETE FROM Game
                                        WHERE title = (?) COLLATE NOCASE""", (game_title,))
            self._conn.commit()
            
            self._notify_observer(f"The game '{removed_game}' has been successfully deleted", "success")
            self._ensure_backup()
        except Exception as e:
            self._notify_observer(f"An unexpected error occured while removing the game '{self._get_specific_game(game_title)}' from the save file. Exception: {e}", "error")
    
    
    def delete_boss(self, boss_name: str, game_title: str) -> None:
        if not self._get_specific_game_exists(game_title):
            self._notify_observer(f"The game '{game_title}' you selected to delete a boss from does not exists in the save file", "indication")
            return
        elif not self.get_specific_boss_exists(boss_name, game_title):
            self._notify_observer(f"The boss '{boss_name}' you wish to delete does not exists in the game '{self._get_specific_game(game_title)}' in the save file", "indication")
            return
        
        try:
            removed_boss: str = self._get_specific_boss(boss_name, game_title)
            
            self._cursor.execute("""DELETE FROM Boss
                                        WHERE name = (?) COLLATE NOCASE and gameId = (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE)""", (boss_name, game_title))
            self._conn.commit()
            
            self._notify_observer(f"The boss '{removed_boss}' of game '{self._get_specific_game(game_title)}' was removed", "success")
            self._ensure_backup()
        except Exception as e:
            self._notify_observer(f"An unexpected error occured while removing the boss '{self._get_specific_boss(boss_name, game_title)}' from game '{self._get_specific_game(game_title)}' the save file. Exception: {e}", "error")
    
    
    def get_bosses_from_game_by(self, game_title: str, sort_filter: str, order_filter: str) -> list[tuple]:
        allowed_sort_filters: list[str] = ["id", "deaths", "requiredTime"]
        allowed_order_filters: list[str] = ["desc", "asc"]
        
        if sort_filter not in allowed_sort_filters:
            self._notify_observer(f"Illegal sort filter '{sort_filter}' used", "indication")
            return
        elif order_filter.lower() not in allowed_order_filters:
            self._notify_observer(f"Illegal order filter '{order_filter}' used", "indication")
            return
        elif not self._get_specific_game_exists(game_title):
            self._notify_observer(f"The game '{game_title}' you selected all bosses from does not exists in the save file", "indication")
            return
        
        self._cursor.execute(f"""SELECT b.name, b.deaths, b.requiredTime FROM Boss b
                                    JOIN Game g on b.gameId = g.id
                                    WHERE g.title = (?) COLLATE NOCASE
                                    ORDER BY b.{sort_filter} {order_filter}""", (game_title,))
        selection: list[tuple] = self._cursor.fetchall()
        
        if not selection:
            self._notify_observer(f"There are no bosses linked to the game '{self._get_specific_game(game_title)}'", "indication")
        
        return selection
    
    
    def get_all_bosses_by(self, sort_filter: str, order_filter: str) -> list[tuple]:
        allowed_sort_filters: list[str] = ["id", "deaths", "requiredTime"]
        allowed_order_filters: list[str] = ["desc", "asc"]
        
        if sort_filter not in allowed_sort_filters:
            self._notify_observer(f"Illegal sort filter '{sort_filter}' used", "indication")
            return
        elif order_filter.lower() not in allowed_order_filters:
            self._notify_observer(f"Illegal order filter '{order_filter}' used", "indication")
            return
        
        self._cursor.execute(f"""SELECT b.name, g.title, b.deaths, b.requiredTime FROM Boss b
                                    JOIN Game g ON b.gameId = g.id
                                    ORDER BY b.{sort_filter} {order_filter}""")
        selection: list[tuple] = self._cursor.fetchall()
        
        if not selection:
            self._notify_observer(f"There are no bosses in the save file so far", "indication")
        
        return selection
    
    
    def get_all_games(self, sort_filter: str, order_filter: str) -> list[tuple]:
        allowed_sort_filters: list[str] = ["gameId", "deaths", "requiredTime"]
        allowed_order_filters: list[str] = ["desc", "asc"]
        
        if sort_filter not in allowed_sort_filters:
            self._notify_observer(f"Illegal sort filter '{sort_filter}' used", "indication")
            return
        elif order_filter.lower() not in allowed_order_filters:
            self._notify_observer(f"Illegal order filter '{order_filter}' used", "indication")
            return
        
        self._cursor.execute(f"""SELECT g.title, SUM(b.deaths), SUM(b.requiredTime) FROM Game g
                                    JOIN Boss b ON b.gameId = g.id
                                    GROUP BY g.title
                                    ORDER BY b.{sort_filter} {order_filter}""")
        selection: list[tuple] = self._cursor.fetchall()
        
        if not selection:
            self._notify_observer(f"There are no games in the save file so far", "indication")
        
        return selection
    
    
    def update_boss(self, boss_name: str, game_title: str, deaths: int, required_time: int) -> bool:
        if not self._get_specific_game_exists(game_title):
            self._notify_observer(f"The game '{game_title}' you selected to save the stats to a boss from does not exists in the save file", "indication")
            return False
        elif not self.get_specific_boss_exists(boss_name, game_title):
            self._notify_observer(f"The boss '{boss_name}' you wish to save the stats to does not exists in the game '{self._get_specific_game(game_title)}' in the save file", "indication")
            return False
        
        try:
            self._cursor.execute("""UPDATE Boss
                                        SET deaths = (?), requiredTime = (?)
                                        WHERE name = (?) COLLATE NOCASE and gameId = (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE)""", (deaths, required_time, boss_name, game_title))
            self._conn.commit()
            
            self._notify_observer(f"The boss '{self._get_specific_boss(boss_name, game_title)}' of game '{self._get_specific_game(game_title)}' was updated with the following values: Deaths {deaths}, Req. time {required_time}", "success")
            self._ensure_backup()
            return True
        except Exception as e:
            self._notify_observer(f"An unexpected error occured while saving the stats to the boss '{self._get_specific_boss(boss_name, game_title)}' of game '{self._get_specific_game(game_title)}'. Exception: {e}", "error")
            return False
    
    
    # helper methods below
    
    def _get_specific_game(self, game_title: str, case_insensitive: bool = True) -> str:
        if case_insensitive:
            self._cursor.execute("""SELECT title FROM Game
                                        WHERE title = (?) COLLATE NOCASE""", (game_title,))
        else:
            self._cursor.execute("""SELECT title FROM Game
                                        WHERE title = (?)""", (game_title,))
        
        selection: list[tuple] = self._cursor.fetchone()
        
        if selection is None:
            return
        else:
            return selection[0]
    
    
    def _get_specific_game_exists(self, game_title: str, case_insensitive: bool = True) -> bool:
        selection: str = self._get_specific_game(game_title, case_insensitive)
        
        if selection is None:
            return False
        else:
            return True
    
    
    def _get_specific_boss(self, boss_name: str, game_title: str, case_insensitive: bool = True) -> str:
        if case_insensitive:
            self._cursor.execute("""SELECT b.name FROM Boss b
                                        JOIN Game g ON b.gameId = g.id
                                        WHERE b.name = (?) COLLATE NOCASE and g.title = (?) COLLATE NOCASE""", (boss_name, game_title))
        else:
            self._cursor.execute("""SELECT b.name FROM Boss b
                                        JOIN Game g ON b.gameId = g.id
                                        WHERE b.name = (?) and g.title = (?) COLLATE NOCASE""", (boss_name, game_title))
        
        selection: list[tuple] = self._cursor.fetchone()
        
        if selection is None:
            return
        else:
            return selection[0]
    
    
    def get_specific_boss_exists(self, boss_name: str, game_title: str, case_insensitive: bool = True) -> bool:
        selection: str = self._get_specific_boss(boss_name, game_title, case_insensitive)
        
        if selection is None:
            return False
        else:
            return True
    
    
    def _get_unknown_boss_numbers(self, list_of_unknown_bosses: list[tuple]) -> list[int]:
        unknown_boss_nums: list[int] = []
        
        for boss_name in list_of_unknown_bosses:
            for num in str(boss_name[0]).split():
                if num.isdigit():
                    unknown_boss_nums.append(int(num))
        
        return unknown_boss_nums
    
    
    def _move_boss_operation(self, boss_name: str, game_title: str, new_game_title: str) -> bool:
        try:
            self._cursor.execute("""UPDATE Boss
                                        SET gameId = (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE)
                                        WHERE name = (?) COLLATE NOCASE and gameId = (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE)""", (new_game_title, boss_name, game_title))
            self._conn.commit()
            return True
        except Exception as e:
            self._notify_observer(f"An unexpected error occured while moving the boss '{self._get_specific_boss(boss_name, game_title)}' from '{self._get_specific_game(game_title)}' to '{new_game_title}'. Exception: {e}", "error")
            return False
    
    
    def _rename_boss_operation(self, boss_name: str, game_title: str, new_boss_name: str) -> bool:
        try:
            self._cursor.execute("""UPDATE Boss
                                        SET name = (?)
                                        WHERE name = (?) COLLATE NOCASE and gameId = (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE)""", (new_boss_name, boss_name, game_title))
            self._conn.commit()
            return True
        except Exception as e:
            self._notify_observer(f"An unexpected error occured while renaming the boss '{self._get_specific_boss(boss_name, game_title)}' of game '{self._get_specific_game(game_title)}' to '{new_boss_name}'. Exception: {e}", "error")
            return False
    
    
    def get_specific_boss_deaths(self, boss_name: str, game_title: str) -> int:
        self._cursor.execute("""SELECT b.deaths FROM Boss b
                                    JOIN Game g ON b.gameId = g.id
                                    WHERE b.name = (?) COLLATE NOCASE and g.title = (?) COLLATE NOCASE""", (boss_name, game_title))
        selection: list[tuple] = self._cursor.fetchone()
        
        return selection[0]
    
    
    def get_specific_boss_time(self, boss_name: str, game_title: str) -> int:
        self._cursor.execute("""SELECT b.requiredTime FROM Boss b
                                    JOIN Game g ON b.gameId = g.id
                                    WHERE b.name = (?) COLLATE NOCASE and g.title = (?) COLLATE NOCASE""", (boss_name, game_title))
        selection: list[tuple] = self._cursor.fetchone()
        
        return selection[0]
    
    
    def get_specific_game_avg(self, game_title: str) -> list[tuple]:
        self._cursor.execute("""SELECT 
                                    CASE
                                        WHEN ROUND(AVG(b.deaths), 2) = CAST(AVG(b.deaths) AS INTEGER) THEN CAST(AVG(b.deaths) AS INTEGER)
                                        ELSE ROUND(AVG(b.deaths), 2)
                                    END,
                                    CAST(AVG(b.requiredTime) + 0.5 AS INTEGER) FROM Boss b
                                        JOIN Game g ON b.gameId = g.id
                                        WHERE g.title = (?) COLLATE NOCASE""", (game_title,))
        return self._cursor.fetchall()
    
    
    def get_specific_game_sum(self, game_title: str) -> list[tuple]:
        self._cursor.execute("""SELECT SUM(b.deaths), SUM(b.requiredTime) FROM Boss b
                                    JOIN Game g ON b.gameId = g.id
                                    WHERE g.title = (?) COLLATE NOCASE""", (game_title,))
        return self._cursor.fetchall()
    
    
    def get_all_game_avg(self) -> list[tuple]:
        # CTE (common table expression): tmp selection to use more than one aggregate function on the selection
        self._cursor.execute("""WITH GameTotal AS (
                                    SELECT SUM(b.deaths) AS totalDeaths, SUM(b.requiredTime) AS totalTime FROM Boss b
                                        JOIN Game g on b.gameId = g.id
                                        GROUP BY g.title
                                )
                                SELECT
                                    CASE
                                        WHEN ROUND(AVG(totalDeaths), 2) = CAST(AVG(totalDeaths) AS INTEGER) THEN CAST(AVG(totalDeaths) AS INTEGER)
                                        ELSE ROUND(AVG(totalDeaths), 2)
                                    END,
                                    CAST(AVG(totalTime) + 0.5 AS INTEGER) FROM GameTotal""")
        return self._cursor.fetchall()
    
    
    def get_all_game_sum(self) -> list[tuple]:
        return self.get_all_boss_sum()
    
    
    def get_all_boss_avg(self) -> list[tuple]:
        self._cursor.execute("""SELECT
                                    CASE
                                        WHEN ROUND(AVG(deaths), 2) = CAST(AVG(deaths) AS INTEGER) THEN CAST(AVG(deaths) AS INTEGER)
                                        ELSE ROUND(AVG(deaths), 2)
                                    END,
                                    CAST(AVG(requiredTime) + 0.5 AS INTEGER) FROM Boss""")
        return self._cursor.fetchall()
    
    
    def get_all_boss_sum(self) -> list[tuple]:
        self._cursor.execute("""SELECT SUM(deaths), SUM(requiredTime) FROM Boss""")
        return self._cursor.fetchall()