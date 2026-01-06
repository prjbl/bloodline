from pathlib import Path
from typing import List

from file_io import DatabaseHandler
from infrastructure import Directory, MessageHub

class SaveFile:
    
    def __init__(self):
        self._msg_provider: MessageHub = MessageHub()
        
        self._db_handler: DatabaseHandler = DatabaseHandler(
            db_file_path=SaveFile._DB_FILE_PATH,
            backup_file_path=SaveFile._BACKUP_FILE_PATH,
            latest_version=SaveFile._LATEST_VERSION,
            db_structure=SaveFile._DB_STRUCURE,
            db_updates=self._update_history
        )
    
    
    _DB_FILE: str = "save_file.sqlite"
    _BACKUP_FILE: str = f"{_DB_FILE}.bak"
    _DB_FILE_PATH: Path = Directory.get_persistent_data_path().joinpath(_DB_FILE)
    _BACKUP_FILE_PATH: Path = Directory.get_backup_path().joinpath(_BACKUP_FILE)
    
    _LATEST_VERSION: int = 1
    _DB_STRUCURE: str = """
        CREATE TABLE IF NOT EXISTS Game (
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
        );"""
    
    _UNKNOWN_GAME_TITLE: str = "Unknown Game"
    _UNKNOWN_BOSS_NAME: str = "Unknown Boss"
    
    
    def _update_history(self, curr_version: int) -> None:
        """try:
            if curr_version == 1:
                # update 1
                # increment version number
            elif curr_version == 2:
                # update 2
                # increment version number
            etc.
        except ..."""
    
    
    def close_connection(self) -> None:
        self._db_handler.close_connection()
    
    
    # db manipulation methods below
    
    def get_boss_table_description(self) -> tuple:
        return self._db_handler.get_table_description()
    
    
    def _add_game(self, game_title: str) -> None:
        if self._get_game_exists(game_title):
            return
        
        sql: str = """
            INSERT INTO Game (title)
                VALUES (?)"""
        
        self._execute_and_report_dml(
            sql=sql,
            params=(game_title,),
            success_msg=f"The game '{game_title}' has been added to the save file",
            error_msg=f"An unexpected error occured while adding the game '{game_title}' to the save file",
            ensure_backup=False
        )
    
    
    def add_boss(self, boss_name: str, game_title: str, ensure_backup: bool = True) -> bool:
        if self.get_boss_exists(boss_name, game_title):
            self._msg_provider.invoke(f"The boss '{self._get_cased_boss_name(boss_name, game_title)}' of game '{self._get_cased_game_title(game_title)}' already exists in the save file", "invalid")
            return False
        
        self._add_game(game_title)
        
        sql: str = """
            INSERT INTO Boss (name, gameId)
                VALUES ((?), (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE))"""
        
        return self._execute_and_report_dml(
            sql=sql,
            params=(boss_name, game_title),
            success_msg=f"The boss '{boss_name}' has been added to the game '{self._get_cased_game_title(game_title) if self._get_game_exists(game_title) else game_title}'",
            error_msg=f"An unexpected error occured while adding the boss '{boss_name}' to '{self._get_cased_game_title(game_title) if self._get_game_exists(game_title) else game_title}'",
            ensure_backup=ensure_backup
        )
    
    
    def add_preset(self, loaded_preset: dict) -> None:
        changes_made: bool = False
        
        for game_title, list_of_bosses in loaded_preset.items():
            for boss_name in list_of_bosses:
                boss_added: bool = self.add_boss(boss_name, game_title, ensure_backup=False)
                changes_made = changes_made or boss_added # if changed_made is True onces, it keeps the True state even if boss_added is False
        
        if changes_made:
            self._db_handler.ensure_backup()
    
    
    def add_unknown(self) -> None:
        sql: str = """
            SELECT b.name FROM Boss b
                JOIN Game g ON b.gameId = g.id
                WHERE b.name LIKE (?) || '%' AND g.title = (?)"""
        
        list_of_unknown_bosses: List[tuple] = self._db_handler.fetch(sql, SaveFile._UNKNOWN_BOSS_NAME, SaveFile._UNKNOWN_GAME_TITLE)
        unknown_boss_nums: List[int] = self._get_unknown_boss_nums(list_of_unknown_bosses)
        
        boss_name_exists: bool = True
        iterator: int = 0
        
        while boss_name_exists:
            iterator += 1
            
            if iterator in unknown_boss_nums:
                continue
            
            boss_name_exists = False
            self.add_boss(f"{SaveFile._UNKNOWN_BOSS_NAME} {iterator}", SaveFile._UNKNOWN_GAME_TITLE)
    
    
    def identify_boss(self, unknown_boss_num: str, new_boss_name: str, new_game_title: str) -> None:
        if not self._get_game_exists(SaveFile._UNKNOWN_GAME_TITLE):
            self._msg_provider.invoke(f"The game '{SaveFile._UNKNOWN_GAME_TITLE}' you want to identify a boss from does not exist in the save file so far", "invalid")
            return
        elif not self.get_boss_exists(f"{SaveFile._UNKNOWN_BOSS_NAME} {unknown_boss_num}", SaveFile._UNKNOWN_GAME_TITLE):
            self._msg_provider.invoke(f"The boss '{SaveFile._UNKNOWN_BOSS_NAME} {unknown_boss_num}' you selected to identify does not exist in the game {SaveFile._UNKNOWN_GAME_TITLE}", "invalid")
            return
        elif not self._get_game_exists(new_game_title):
            self._msg_provider.invoke(f"The game '{new_game_title}' you selected to link the boss to does not exist in the save file so far", "invalid")
            return
        elif self.get_boss_exists(new_boss_name, new_game_title):
            self._msg_provider.invoke(f"The boss '{self._get_cased_boss_name(new_boss_name, new_game_title)}' already exists in the game '{self._get_cased_game_title(new_game_title)}'", "invalid")
            return
        
        if not self._rename_boss_operation(f"{SaveFile._UNKNOWN_BOSS_NAME} {unknown_boss_num}", SaveFile._UNKNOWN_GAME_TITLE, new_boss_name, False):
            return
        if not self._move_boss_operation(new_boss_name, SaveFile._UNKNOWN_GAME_TITLE, new_game_title):
            return
        
        self._msg_provider.invoke(f"The boss '{SaveFile._UNKNOWN_BOSS_NAME} {unknown_boss_num}' was identified as '{new_boss_name}' from game '{self._get_cased_game_title(new_game_title)}'", "success")
    
    
    def rename_boss(self, boss_name: str, game_title: str, new_boss_name: str) -> None:
        if not self._get_game_exists(game_title):
            self._msg_provider.invoke(f"The game '{game_title}' you selected does not exist in the save file", "invalid")
            return
        elif not self.get_boss_exists(boss_name, game_title):
            self._msg_provider.invoke(f"The boss '{boss_name}' you wish to rename does not exist in the game '{self._get_cased_game_title(game_title)}' in the save file so far", "invalid")
            return
        elif self.get_boss_exists(new_boss_name, game_title):
            self._msg_provider.invoke(f"The boss '{self._get_cased_boss_name(new_boss_name, game_title)}' already exists in the game '{self._get_cased_game_title(game_title)}'", "invalid")
            return
        
        old_boss_name: str = self._get_cased_boss_name(boss_name, game_title)
        
        if not self._rename_boss_operation(boss_name, game_title, new_boss_name):
            return
        
        self._msg_provider.invoke(f"The boss '{old_boss_name}' of game '{self._get_cased_game_title(game_title)}' was renamed to '{new_boss_name}'", "success")
    
    
    def rename_game(self, game_title: str, new_game_title: str) -> None:
        if not self._get_game_exists(game_title):
            self._msg_provider.invoke(f"The game '{game_title}' you wish to rename does not exist in the save file so far", "invalid")
            return
        elif self._get_game_exists(new_game_title):
            self._msg_provider.invoke(f"The game '{self._get_cased_game_title(new_game_title)}' already exist in the save file", "invalid")
            return
        
        sql: str = """
            UPDATE Game
                SET title = (?)
                WHERE title = (?) COLLATE NOCASE"""
        
        old_game_title: str = self._get_cased_game_title(game_title)
        
        self._execute_and_report_dml(
            sql=sql,
            params=(new_game_title, game_title),
            success_msg=f"The game '{old_game_title}' was renamed to '{new_game_title}'",
            error_msg=f"An unexpected error occured while renaming the game '{old_game_title}' to '{new_game_title}'."
        )
    
    
    def move_boss(self, boss_name: str, game_title: str, new_game_title: str) -> None:
        if not self._get_game_exists(game_title):
            self._msg_provider.invoke(f"The game '{game_title}' you selected to move the boss from does not exist in the save file so far", "invalid")
            return
        elif not self.get_boss_exists(boss_name, game_title):
            self._msg_provider.invoke(f"The boss '{boss_name}' you selected to move does not exist in the game '{self._get_cased_game_title(game_title)}'", "invalid")
            return
        elif not self._get_game_exists(new_game_title):
            self._msg_provider.invoke(f"The game '{new_game_title}' you selected to be moved to does not exist in the save file so far", "invalid")
            return
        elif self.get_boss_exists(boss_name, new_game_title):
            self._msg_provider.invoke(f"The boss '{self._get_cased_boss_name(boss_name, game_title)}' already exist in the game '{self._get_cased_game_title(new_game_title)}'", "invalid")
            return
        
        old_game_title: str = self._get_cased_game_title(game_title)
        
        if not self._move_boss_operation(boss_name, game_title, new_game_title):
            return
        
        self._msg_provider.invoke(f"The boss '{self._get_cased_boss_name(boss_name, new_game_title)}' was moved from game '{old_game_title}' to '{self._get_cased_game_title(new_game_title)}'", "success")
    
    
    def delete_game(self, game_title: str) -> None:
        if not self._get_game_exists(game_title):
            self._msg_provider.invoke(f"The game '{game_title}' you wish to delete does not exist in the save file", "invalid")
            return
        
        sql: str = """
            DELETE FROM Game
                WHERE title = (?) COLLATE NOCASE"""
        
        removed_game: str = self._get_cased_game_title(game_title)
        
        self._execute_and_report_dml(
            sql=sql,
            params=(game_title,),
            success_msg=f"The game '{removed_game}' has been successfully deleted",
            error_msg=f"An unexpected error occured while removing the game '{self._get_cased_game_title(game_title)}' from the save file."
        )
    
    
    def delete_boss(self, boss_name: str, game_title: str) -> None:
        if not self._get_game_exists(game_title):
            self._msg_provider.invoke(f"The game '{game_title}' you selected to delete a boss from does not exist in the save file", "invalid")
            return
        elif not self.get_boss_exists(boss_name, game_title):
            self._msg_provider.invoke(f"The boss '{boss_name}' you wish to delete does not exist in the game '{self._get_cased_game_title(game_title)}'", "invalid")
            return
        
        sql: str = """
            DELETE FROM Boss
                WHERE name = (?) COLLATE NOCASE AND gameId = (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE)"""
        
        removed_boss: str = self._get_cased_boss_name(boss_name, game_title)
        
        self._execute_and_report_dml(
            sql=sql,
            params=(boss_name, game_title),
            success_msg=f"The boss '{removed_boss}' of game '{self._get_cased_game_title(game_title)}' was removed",
            error_msg=f"An unexpected error occured while removing the boss '{self._get_cased_boss_name(boss_name, game_title)}' from game '{self._get_cased_game_title(game_title)}'."
        )
    
    
    def update_boss(self, boss_name: str, game_title: str, deaths: int | None, required_time: int | None) -> bool:
        if not self._get_game_exists(game_title):
            self._msg_provider.invoke(f"The game '{game_title}' you selected to save the stats to a boss from does not exist in the save file", "invalid")
            return False
        elif not self.get_boss_exists(boss_name, game_title):
            self._msg_provider.invoke(f"The boss '{boss_name}' you wish to save the stats to does not exist in the game '{self._get_cased_game_title(game_title)}'", "invalid")
            return False
        
        sql: str = """
            UPDATE Boss
                SET deaths = (?), requiredTime = (?)
                WHERE name = (?) COLLATE NOCASE AND gameId = (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE)"""
        
        return self._execute_and_report_dml(
            sql=sql,
            params=(deaths, required_time, boss_name, game_title),
            success_msg=f"The boss '{self._get_cased_boss_name(boss_name, game_title)}' of game '{self._get_cased_game_title(game_title)}' was updated with the following values: Deaths {deaths}, Req. time {required_time}",
            error_msg=f"An unexpected error occured while saving the stats to the boss '{self._get_cased_boss_name(boss_name, game_title)}' of game '{self._get_cased_game_title(game_title)}'."
        )
    
    
    # db selection methods below
    
    def get_all_games_by(self, sort_filter: str, order_filter: str) -> List[tuple]:
        allowed_sort_filters: List[str] = ["gameId", "deaths", "requiredTime"]
        
        if not self._validate_filters(sort_filter, order_filter, allowed_sort_filters):
            return []
        
        sql: str = f"""
            SELECT g.title, SUM(b.deaths), SUM(b.requiredTime) FROM Game g
                JOIN Boss b ON b.gameId = g.id
                GROUP BY g.title
                ORDER BY b.{sort_filter} {order_filter}"""
        
        fetched_list_of_games: List[tuple] = self._db_handler.fetch(sql)
        
        if not fetched_list_of_games:
            self._msg_provider.invoke("There are no games in the save file so far", "invalid")
        return fetched_list_of_games
    
    
    def get_all_bosses_by(self, sort_filter: str, order_filter: str) -> List[tuple]:
        allowed_sort_filters: List[str] = ["id", "deaths", "requiredTime"]
        
        if not self._validate_filters(sort_filter, order_filter, allowed_sort_filters):
            return []
        
        sql: str = f"""
            SELECT b.name, g.title, b.deaths, b.requiredTime FROM Boss b
                JOIN Game g ON b.gameId = g.id
                ORDER BY b.{sort_filter} {order_filter}"""
        
        fetched_list_of_bosses: List[tuple] = self._db_handler.fetch(sql)
        
        if not fetched_list_of_bosses:
            self._msg_provider.invoke("There are no bosses in the save file so far", "invalid")
        return fetched_list_of_bosses
    
    
    def get_bosses_from_game_by(self, game_title: str, sort_filter: str, order_filter: str) -> List[tuple]:
        allowed_sort_filters: List[str] = ["id", "deaths", "requiredTime"]
        
        if not self._validate_filters(sort_filter, order_filter, allowed_sort_filters):
            return []
        elif not self._get_game_exists(game_title):
            self._msg_provider.invoke(f"The game '{game_title}' you selected all the bosses from does not exists in the save file", "invalid")
            return []
        
        sql: str = f"""
            SELECT b.name, b.deaths, b.requiredTime FROM Boss b
                JOIN Game g ON b.gameId = g.id
                WHERE g.title = (?) COLLATE NOCASE
                ORDER BY b.{sort_filter} {order_filter}"""
        
        fetched_list_of_bosses: List[tuple] = self._db_handler.fetch(sql, game_title)
        
        if not fetched_list_of_bosses:
            self._msg_provider.invoke(f"There are no bosses linked to the game '{self._get_cased_game_title(game_title)}'", "invalid")
        return fetched_list_of_bosses
    
    
    def get_boss_deaths(self, boss_name: str, game_title: str) -> int | None:
        sql: str = """
            SELECT b.deaths FROM Boss b
                JOIN Game g ON b.gameId = g.id
                WHERE b.name = (?) COLLATE NOCASE and g.title = (?) COLLATE NOCASE"""
        
        fetched_boss_deaths: List[tuple] = self._db_handler.fetch(sql, boss_name, game_title)
        
        if not fetched_boss_deaths:
            return None
        return fetched_boss_deaths[0][0]
    
    
    def get_boss_time(self, boss_name: str, game_title: str) -> int | None:
        sql: str = """
            SELECT b.requiredTime FROM Boss b
                JOIN Game g ON b.gameId = g.id
                WHERE b.name = (?) COLLATE NOCASE and g.title = (?) COLLATE NOCASE"""
        
        fetched_boss_time: List[tuple] = self._db_handler.fetch(sql, boss_name, game_title)
        
        if not fetched_boss_time:
            return None
        return fetched_boss_time[0][0]
    
    
    def get_all_games_sum(self) -> List[tuple]:
        return self.get_all_bosses_sum()
    
    
    def get_all_games_avg(self) -> List[tuple]:
        # CTE (common table expression): tmp selection to use more than one aggregate function on the selection
        sql: str = """
            WITH GameTotal AS (
                SELECT SUM(b.deaths) AS totalDeaths, SUM(b.requiredTime) AS totalTime FROM Boss b
                    JOIN Game g ON b.gameId = g.id
                    GROUP BY g.title
                )
                SELECT
                    CASE
                        WHEN ROUND(AVG(totalDeaths), 2) = CAST(AVG(totalDeaths) AS INTEGER) THEN CAST(AVG(totalDeaths) AS INTEGER)
                        ELSE ROUND(AVG(totalDeaths), 2)
                    END,
                    CAST(AVG(totalTime) + 0.5 AS INTEGER) FROM GameTotal"""
        
        fetched_all_game_avg: List[tuple] = self._db_handler.fetch(sql)
        return fetched_all_game_avg
    
    
    def get_game_sum(self, game_title: str) -> List[tuple]:
        sql: str = """
            SELECT SUM(b.deaths), SUM(b.requiredTime) FROM Boss b
                JOIN Game g ON b.gameId = g.id
                WHERE g.title = (?) COLLATE NOCASE"""
        
        fetched_game_sum: List[tuple] = self._db_handler.fetch(sql, game_title)
        return fetched_game_sum
    
    
    def get_game_avg(self, game_title: str) -> List[tuple]:
        sql: str = """
            SELECT
                CASE
                    WHEN ROUND(AVG(b.deaths), 2) = CAST(AVG(b.deaths) AS INTEGER) THEN CAST(AVG(b.deaths) AS INTEGER)
                    ELSE ROUND(AVG(b.deaths), 2)
                END,
                CAST(AVG(b.requiredTime) + 0.5 AS INTEGER) FROM Boss b
                    JOIN Game g ON b.gameId = g.id
                    WHERE g.title = (?) COLLATE NOCASE"""
        
        fetched_game_avg: List[tuple] = self._db_handler.fetch(sql, game_title)
        return fetched_game_avg
    
    
    def get_all_bosses_sum(self) -> List[tuple]:
        sql: str = """
            SELECT SUM(deaths), SUM(requiredTime) FROM Boss"""
        
        fetched_all_bosses_sum: List[tuple] = self._db_handler.fetch(sql)
        return fetched_all_bosses_sum
    
    
    def get_all_bosses_avg(self) -> List[tuple]:
        sql: str = """
            SELECT
                CASE
                    WHEN ROUND(AVG(deaths), 2) = CAST(AVG(deaths) AS INTEGER) THEN CAST(AVG(deaths) AS INTEGER)
                    ELSE ROUND(AVG(deaths), 2)
                END,
                CAST(AVG(requiredTime) + 0.5 AS INTEGER) FROM Boss"""
        
        fetched_all_bosses_avg: List[tuple] = self._db_handler.fetch(sql)
        return fetched_all_bosses_avg
    
    
    # helper methods below
    
    def _execute_and_report_dml(self, sql: str, params: tuple, success_msg: str | None, error_msg: str, ensure_backup: bool = True) -> bool:
        try:
            self._db_handler.execute_dml(sql, *params)
            
            if success_msg:
                self._msg_provider.invoke(success_msg, "success")
            
            if ensure_backup:
                self._db_handler.ensure_backup()
            return True
        except Exception as e:
            self._msg_provider.invoke(f"{error_msg}. Exception: {e}", "error")
            return False
    
    
    def _get_game_exists(self, game_title: str) -> bool:
        fetched_game_title: str = self._get_cased_game_title(game_title)
        
        if fetched_game_title is None:
            return False
        return True
    
    
    def _get_cased_game_title(self, game_title: str) -> str | None:
        sql: str = """
            SELECT title FROM Game
                WHERE title = (?) COLLATE NOCASE"""
        
        fetched_game_title: List[tuple] = self._db_handler.fetch(sql, game_title)
        
        if not fetched_game_title:
            return None
        return fetched_game_title[0][0]
    
    
    def get_boss_exists(self, boss_name: str, game_title: str) -> bool:
        fetched_boss_name: str = self._get_cased_boss_name(boss_name, game_title)
        
        if fetched_boss_name is None:
            return False
        return True
    
    
    def _get_cased_boss_name(self, boss_name: str, game_title: str) -> str | None:
        sql: str = """
            SELECT b.name FROM Boss b
                JOIN Game g ON b.gameId = g.id
                WHERE b.name = (?) COLLATE NOCASE AND g.title = (?) COLLATE NOCASE"""
        
        fetched_boss_name: List[tuple] = self._db_handler.fetch(sql, boss_name, game_title)
        
        if not fetched_boss_name:
            return None
        return fetched_boss_name[0][0]
    
    
    @classmethod
    def _get_unknown_boss_nums(cls, list_of_unknown_bosses: List[tuple]) -> List[int]:
        unknown_boss_nums: List[int] = []
        
        for boss_name in list_of_unknown_bosses:
            parts_of_name: List[str] = str(boss_name[0]).split(cls._UNKNOWN_BOSS_NAME)
            name_index: str = parts_of_name[1].strip()
            
            if not name_index or not name_index.isdigit():
                continue
            
            unknown_boss_nums.append(int(name_index))
        return unknown_boss_nums
    
    
    def _rename_boss_operation(self, boss_name: str, game_title: str, new_boss_name: str, ensure_backup: bool = True) -> bool:
        sql: str = """
            UPDATE Boss
                SET name = (?)
                WHERE name = (?) COLLATE NOCASE AND gameId = (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE)"""
        
        return self._execute_and_report_dml(
            sql=sql,
            params=(new_boss_name, boss_name, game_title),
            success_msg=None,
            error_msg=f"An unexpected error occured while renaming the boss '{self._get_cased_boss_name(boss_name, game_title)}' of game '{self._get_cased_game_title(game_title)}' to '{new_boss_name}'.",
            ensure_backup=ensure_backup
        )
    
    
    def _move_boss_operation(self, boss_name: str, game_title: str, new_game_title: str, ensure_backup: bool = True) -> bool:
        sql: str = """
            UPDATE Boss
                SET gameId = (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE)
                WHERE name = (?) COLLATE NOCASE and gameId = (SELECT id FROM Game WHERE title = (?) COLLATE NOCASE)"""
        
        return self._execute_and_report_dml(
            sql=sql,
            params=(new_game_title, boss_name, game_title),
            success_msg=None,
            error_msg=f"An unexpected error occured while moving the boss '{self._get_cased_boss_name(boss_name, game_title)}' from '{self._get_cased_game_title(game_title)}' to '{new_game_title}'.",
            ensure_backup=ensure_backup
        )
    
    
    def _validate_filters(self, sort_filter: str, order_filter: str, allowed_sort_filters: List[str]) -> bool:
        allowed_order_filters: List[str] = ["desc", "asc"]
        
        if sort_filter not in allowed_sort_filters:
            self._msg_provider.invoke(f"Illegal sort filter '{sort_filter}' used", "invalid")
            return False
        elif order_filter.lower() not in allowed_order_filters:
            self._msg_provider.invoke(f"Illegal order filter '{order_filter}' used", "invalid")
            return False
        return True