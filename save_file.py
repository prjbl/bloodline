from os import remove
from shutil import copy2
from sqlite3 import Connection, Cursor, connect, DatabaseError

from directory import Directory

class SaveFile:
    
    def __init__(self):
        self._conn: Connection = None
        self._cursor: Cursor = None
        self._observer: any = None
        
        self._open_connection()
    
    
    _dir: Directory = Directory()
    
    _DB_FILE_NAME: str = "save_file.db"
    _BACKUP_FILE_NAME: str = "save_file_backup.db"
    
    _UNKNOWN_GAME_TITLE: str = "Unknown Game"
    _UNKNOWN_BOSS_NAME: str = "Unknown Boss"
    
    
    def setup_db_and_observer(self, observer: any) -> None:
        self._observer = observer
        
        self._create_tables() # setup had to be outsourced to after the observer has been set, as its required for the setup process
    
    
    def _notify_observer(self, text: str, text_type: str) -> None:
        self._observer(text, text_type)
    
    
    def _open_connection(self) -> None:
        self._conn = connect(self._dir.get_persistent_data_path().joinpath(self._DB_FILE_NAME))
        self._conn.execute("PRAGMA foreign_keys = ON") # activates foreign key restriction
        self._cursor = self._conn.cursor()
    
    
    def _create_tables(self) -> None:
        try:
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
            
            if not self._dir.get_backup_path().joinpath(self._BACKUP_FILE_NAME).exists():
                self._create_backup()
        except DatabaseError:
            self._notify_observer(f"The file '{self._DB_FILE_NAME}' is corrupted. This save file will be deleted and the last backup file is beeing loaded", "error")
            
            try:
                self.close_connection()
                remove(self._dir.get_persistent_data_path().joinpath(self._DB_FILE_NAME))
                self._load_backup()
                self._open_connection()
                self._notify_observer("Whole backuping process was successful", "success")
            except Exception as e:
                self._notify_observer(f"Failed to load '{self._BACKUP_FILE_NAME}'. Exception: {e}", "error")
    
    
    def _create_backup(self) -> None:
        backup_exists: bool = self._dir.get_backup_path().joinpath(self._BACKUP_FILE_NAME).exists()
        
        try:
            backup_conn: Connection = connect(self._dir.get_backup_path().joinpath(self._BACKUP_FILE_NAME))
            self._conn.backup(backup_conn)
            backup_conn.close()
            
            if not backup_exists:
                self._notify_observer("Backup was created", "normal")
            else:
                self._notify_observer("Backup was updated", "normal")
        except DatabaseError:
            self._notify_observer(f"The backup file '{self._BACKUP_FILE_NAME}' is corrupted. An attempt is made to re-initialized file", "error")
            
            try:
                backup_conn.close()
                remove(self._dir.get_backup_path().joinpath(self._BACKUP_FILE_NAME))
                self._create_backup()
            except Exception as e:
                self._notify_observer(f"Failed to re-initialize '{self._BACKUP_FILE_NAME}'. Exception: {e}", "error")
    
    
    def _load_backup(self) -> None:
        copy2(self._dir.get_backup_path().joinpath(self._BACKUP_FILE_NAME), self._dir.get_persistent_data_path().joinpath(self._DB_FILE_NAME))
        self._notify_observer("Loading backup was successful", "success")
    
    
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
    
    
    def add_boss(self, boss_name: str, game_title: str) -> None:
        if self.get_specific_boss_exists(boss_name, game_title):
            self._notify_observer(f"The boss '{self._get_specific_boss(boss_name, game_title)}' of game '{self._get_specific_game(game_title)}' already exists in the save file", "indication")
            return
        
        self._add_game(game_title)
        
        try:
            self._cursor.execute("""INSERT INTO Boss (name, gameId)
                                        VALUES (?, (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE))""", (boss_name, game_title))
            self._conn.commit()
            
            self._notify_observer(f"The boss '{boss_name}' of game '{self._get_specific_game(game_title) if self._get_specific_game_exists(game_title) else game_title}' has been added to the save file", "normal")
            self._create_backup()
        except Exception as e:
            self._notify_observer(f"An unexpected error occured while adding the boss '{boss_name}' to '{game_title}'. Exception: {e}", "error")
    
    
    def add_unknown(self) -> None:
        self._add_game(self._UNKNOWN_GAME_TITLE)
        self.add_boss(f"{self._UNKNOWN_BOSS_NAME} {self._get_unknown_bosses_count()}", self._UNKNOWN_GAME_TITLE)
    
    
    def identify_boss(self, boss_name: str, new_boss_name: str, new_game_title: str) -> None:
        self.rename_boss(boss_name, self._UNKNOWN_GAME_TITLE, new_boss_name)
        self.move_boss(new_boss_name, self._UNKNOWN_GAME_TITLE, new_game_title)
    
    
    def move_boss(self, boss_name: str, game_title: str, new_game_title: str) -> None:
        if not self._get_specific_game_exists(game_title):
            self._notify_observer(f"The game '{game_title}' you selected to move does not exists in the save file so far", "indication")
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
        
        try:
            old_game_title: str = self._get_specific_game(game_title)
            
            self._cursor.execute("""UPDATE Boss
                                        SET gameId = (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE)
                                        WHERE name = (?) COLLATE NOCASE and gameId = (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE)""", (new_game_title, boss_name, game_title))
            self._conn.commit()
            
            self._notify_observer(f"The boss '{self._get_specific_boss(boss_name, new_game_title)}' was moved from game '{old_game_title}' to '{self._get_specific_game(new_game_title)}'", "success")
        except Exception as e:
            self._notify_observer(f"An unexpected error occured while moving the boss '{self._get_specific_boss(boss_name, game_title)}' from '{self._get_specific_game(game_title)}' to '{new_game_title}'. Exception: {e}", "error")
    
    
    def rename_game(self, game_title: str, new_game_title: str) -> None:
        if not self._get_specific_game_exists(game_title):
            self._notify_observer(f"The game '{game_title}' you wish to rename does not exists in the save file so far", "indication")
            return
        
        try:
            old_game_title: str = self._get_specific_game(game_title)
            
            self._cursor.execute("""UPDATE Game
                                        SET title = (?)
                                        WHERE title = (?) COLLATE NOCASE""", (new_game_title, game_title))
            self._conn.commit()
            
            self._notify_observer(f"The game '{old_game_title}' was renamed to '{new_game_title}'", "success")
        except Exception as e:
            self._notify_observer(f"An unexpected error occured while renaming the game '{self._get_specific_game(game_title)}' to '{new_game_title}'. Exception: {e}", "error")
    
    
    def rename_boss(self, boss_name: str, game_title: str, new_boss_name: str) -> None:
        if not self.get_specific_boss_exists(boss_name, game_title):
            self._notify_observer(f"The boss '{boss_name}' you wish to rename does not exists in in the game '{self._get_specific_game(game_title)}' in the save file so far", "indication")
            return
        
        try:
            old_boss_name: str = self._get_specific_boss(boss_name, game_title)
            
            self._cursor.execute("""UPDATE Boss
                                        SET name = (?)
                                        WHERE name = (?) COLLATE NOCASE and gameId = (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE)""", (new_boss_name, boss_name, game_title))
            self._conn.commit()
            
            self._notify_observer(f"The boss '{old_boss_name}' of game '{self._get_specific_game(game_title)}' was renamed to '{new_boss_name}'", "success")
        except Exception as e:
            self._notify_observer(f"An unexpected error occured while renaming the boss '{self._get_specific_boss(boss_name, game_title)}' of game '{self._get_specific_game(game_title)}' to '{new_boss_name}'. Exception: {e}", "error")
    
    
    def get_all_bosses_by_id(self) -> list:
        self._cursor.execute("""SELECT b.name, g.title, b.deaths, b.requiredTime FROM Boss b
                                    JOIN Game g ON b.gameId = g.id
                                    ORDER BY b.id ASC""")
        return self._cursor.fetchall()
    
    
    # helper methods below
    
    def _get_specific_game(self, game_title: str) -> str:
        self._cursor.execute("""SELECT title FROM Game
                                    WHERE title = (?) COLLATE NOCASE""", (game_title,))
        selection: list[tuple] = self._cursor.fetchone()
        
        if selection is None:
            return
        else:
            return selection[0]
    
    
    def _get_specific_game_exists(self, game_title: str) -> bool:
        selection: str = self._get_specific_game(game_title)
        
        if selection is None:
            return False
        else:
            return True
    
    
    def _get_specific_boss(self, boss_name: str, game_title: str) -> str:
        self._cursor.execute("""SELECT name FROM Boss
                                    WHERE name = (?) COLLATE NOCASE and gameId = (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE)""", (boss_name, game_title))
        selection: list[tuple] = self._cursor.fetchone()
        
        if selection is None:
            return
        else:
            return selection[0]
    
    
    def get_specific_boss_exists(self, boss_name: str, game_title: str) -> bool:
        selection: str = self._get_specific_boss(boss_name, game_title)
        
        if selection is None:
            return False
        else:
            return True
    
    
    def _get_unknown_bosses_count(self) -> int:
        self._cursor.execute("""SELECT COUNT(b.name) FROM Boss b
                                    JOIN Game g ON b.gameId = g.id
                                    WHERE g.title = (?)""", (self._UNKNOWN_GAME_TITLE,))
        return self._cursor.fetchone()[0] + 1 # +1 so the first boss starts at 1 and not 0
    
    
    def get_specific_boss_deaths(self, boss_name: str, game_title: str) -> int:
        self._cursor.execute("""SELECT deaths FROM Boss
                                    WHERE name = (?) COLLATE NOCASE and gameId = (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE)""", (boss_name, game_title))
        selection: list[tuple] = self._cursor.fetchone()
        
        if selection[0] is None:
            return 0
        else:
            return selection[0]
    
    
    def get_specific_boss_time(self, boss_name: str, game_title: str) -> int:
        self._cursor.execute("""SELECT requiredTime FROM Boss
                                    WHERE name = (?) COLLATE NOCASE and gameId = (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE)""", (boss_name, game_title))
        selection: list[tuple] = self._cursor.fetchone()
        
        if selection[0] is None:
            return 0
        else:
            return selection[0]
    
    
    
    
    
    
    
    

    
    

    

    
    
    
    
    
    def delete_game(self, title: str) -> None:
        game_exists: bool = self._get_specific_game(title)
        
        if game_exists:
            self._cursor.execute("""DELETE FROM Game
                                        WHERE title = (?)""", (title,))
            self._conn.commit()
            self._notify_observer(f"The game '{title}' has been deleted successfully", "success")
            self._create_backup()
        else:
            self._notify_observer(f"The game '{title}' does not exists in the save file", "indication")
    
    
    def delete_boss(self, boss_name: str, game_title: str) -> None:
        boss_exists: bool = self._get_specific_boss(boss_name, game_title)
        
        if boss_exists:
            self._cursor.execute("""DELETE FROM Boss
                                        WHERE name = (?) and gameTitle = (?)""", (boss_name, game_title))
            self._conn.commit()
            self._notify_observer(f"The boss '{boss_name}' from game '{game_title}' has been deleted successfully", "success")
            self._create_backup()
        else:
            self._notify_observer(f"The boss '{boss_name}' from game '{game_title}' does not exists in the save file", "indication")
    
    
    def get_all_games(self) -> list[str]:
        self._cursor.execute("""SELECT * FROM Game""")
        
        selection: list[str] = self._cursor.fetchall()
        
        if not selection:
            self._notify_observer("Error: There are no games in the save file so far", "error")
            return []
        else:
            cleaned_selection: list[str] = []
            
            for item_tuple in selection:
                cleaned_selection.extend(item_tuple)
            
            return cleaned_selection
    
    # order by id (has to be added to the table)
    def get_all_games_new(self) -> list:
        self._cursor.execute("""SELECT g.title, SUM(b.deaths), SUM(b.requiredTime) FROM Game g
                                    JOIN Boss b ON b.gameTitle = g.title
                                    GROUP BY g.title""")
        selection: list = self._cursor.fetchall()
        
        if not selection:
            self._notify_observer("Error: There are no games in the save file so far", "error")
            return []
        else:
            return selection
    
    
    def get_all_games_desc(self) -> list:
        self._cursor.execute("""SELECT g.title, SUM(b.deaths), SUM(b.requiredTime) FROM Game g
                                    JOIN Boss b ON b.gameTitle = g.title
                                    GROUP BY g.title
                                    ORDER BY SUM(b.deaths) DESC""")
        selection: list = self._cursor.fetchall()
        
        if not selection:
            self._notify_observer("Error: There are no games in the save file so far", "error")
            return []
        else:
            return selection
    
    
    def get_all_games_asc(self) -> list:
        self._cursor.execute("""SELECT g.title, SUM(b.deaths), SUM(b.requiredTime) FROM Game g
                                    JOIN Boss b ON b.gameTitle = g.title
                                    GROUP BY g.title
                                    ORDER BY SUM(b.deaths) ASC""")
        selection: list = self._cursor.fetchall()
        
        if not selection:
            self._notify_observer("Error: There are no games in the save file so far", "error")
            return []
        else:
            return selection
    
    
    def get_all_bosses_from_game(self, game_title: str) -> list[str]:
        self._cursor.execute("""SELECT b.name, b.deaths, b.requiredTime FROM Boss b
                                    JOIN Game g ON b.gameTitle = g.title
                                    WHERE g.title = (?)""", (game_title,))
        selection: list[str] = self._cursor.fetchall()
        
        if not selection:
            self._notify_observer(f"Error: There are no bosses linked to the game {game_title} so far", "error")
            return []
        else:
            return selection
    
    
    def get_bosses_from_game_by_deaths(self, game_title: str, filter: str) -> list:
        if filter == "desc":
            self._cursor.execute("""SELECT * FROM Boss b
                                        JOIN Game g ON b.gameTitle = g.title
                                        WHERE g.title = (?)
                                        ORDER BY b.deaths DESC""", (game_title,))
        elif filter == "asc":
            self._cursor.execute("""SELECT * FROM Boss b
                                        JOIN Game g ON b.gameTitle = g.title
                                        WHERE g.title = (?)
                                        ORDER BY b.deaths ASC""", (game_title,))
        
        selection: list = self._cursor.fetchall()
        
        if not selection:
            self._notify_observer(f"There are no bosses linked to the game {game_title} so far", "indication")
            return []
        else:
            return selection
    
    
    def get_bosses_from_game_by_time(self, game_title: str, filter: str) -> list:
        if filter == "desc":
            self._cursor.execute("""SELECT * FROM Boss b
                                        JOIN Game g ON b.gameTitle = g.title
                                        WHERE g.title = (?)
                                        ORDER BY b.requiredTime DESC""", (game_title,))
        elif filter == "asc":
            self._cursor.execute("""SELECT * FROM Boss b
                                        JOIN Game g ON b.gameTitle = g.title
                                        WHERE g.title = (?)
                                        ORDER BY b.requiredTime ASC""", (game_title,))
        
        selection: list = self._cursor.fetchall()
        
        if not selection:
            self._notify_observer(f"There are no bosses linked to the game {game_title} so far", "indication")
            return []
        else:
            return selection
    
    
    def get_all_bosses_by_deaths(self, filter: str) -> list:
        if filter == "desc":
            self._cursor.execute("""SELECT * FROM Boss
                                        ORDER BY deaths DESC""")
        elif filter == "asc":
            self._cursor.execute("""SELECT * FROM Boss
                                        ORDER BY deaths ASC""")
        
        selection: list = self._cursor.fetchall()
        
        if not selection:
            self._notify_observer(f"There are no bosses in the save file so far", "indication")
            return []
        else:
            return selection
    
    
    def get_all_bosses_by_time(self, filter: str) -> list:
        if filter == "desc":
            self._cursor.execute("""SELECT * FROM Boss
                                        ORDER BY requiredTime DESC""")
        elif filter == "asc":
            self._cursor.execute("""SELECT * FROM Boss
                                        ORDER BY requiredTime ASC""")
        
        selection: list = self._cursor.fetchall()
        
        if not selection:
            self._notify_observer(f"There are no bosses in the save file so far", "indication")
            return []
        else:
            return selection
    
    
    def update_boss(self, boss_name: str, game_title: str, deaths: int, required_time: int) -> None:
        self._cursor.execute("""UPDATE Boss
                                    SET deaths = (?), requiredTime = (?)
                                    WHERE name = (?) and gameTitle = (?)""", (deaths, required_time, boss_name, game_title))
        self._conn.commit()
        
        if self._cursor.rowcount == 0:
            self._notify_observer("Nothing was updated because the given value isn't a valid data set in the save file", "error")
        else:
            self._notify_observer(f"The boss '{boss_name}' of game '{game_title}' was updated with the following values: Deaths {deaths}, Req. time {required_time}", None)
            self._create_backup()
    
    
    #def identify_boss(self, unknown_boss: str, unknown_game: str, boss_name: str, game_title: str) -> None:
    #    self._cursor.execute("""SELECT deaths, requiredTime FROM Boss
    #                                WHERE name = (?) and gameTitle = (?)""", (unknown_boss, unknown_game))
    #    stats: list[str] = self._cursor.fetchall()
    #    
    #    self.delete_boss(unknown_boss, unknown_game)
    #    
    #    self.add_boss(boss_name, game_title)
    #    
    #    self.update_boss(boss_name, game_title, stats[0][0], stats[0][1])
    
    
    def get_specific_required_time(self, boss_name: str, game_title: str) -> int:
        self._cursor.execute("""SELECT requiredTime FROM Boss
                                    WHERE name = (?) and gameTitle = (?)""", (boss_name, game_title))
        tmp_selection: list[int] = self._cursor.fetchall()
        
        for item in tmp_selection:
            selection: int = item[0]
        
        if not tmp_selection:
            self._notify_observer(f"Error: There is no time linked to the boss {boss_name} from {game_title} so far", "error")
            return
        else:
            if selection is None:
                return 0
            else:
                return selection