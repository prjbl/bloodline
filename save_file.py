import sqlite3
from directory import dir

class SaveFile:
    
    def __init__(self):
        self._conn: sqlite3.Connection = sqlite3.connect(dir.get_persistent_data_path().joinpath(self._FILE_NAME))
        self._conn.execute('PRAGMA foreign_keys = ON') #
        self._cursor: sqlite3.Cursor = self._conn.cursor()
        self._observer: any = None
    
    
    _FILE_NAME: str = "save_file.db"
    
    
    def setup_db_and_observer(self, observer: any) -> None:
        self._observer = observer
        
        # setup had to be outsourced to after the observer has been set, as its required for the setup process
        self._create_tables()
    
    
    def _notify_observer(self, text: str, text_type: str) -> None:
        self._observer(text, text_type)
    
    
    def _create_tables(self) -> None:
        try:
            self._cursor.execute("""CREATE TABLE IF NOT EXISTS Game (
                                        title TEXT NOT NULL,
                                        PRIMARY KEY (title)
                                )""")
            
            self._cursor.execute("""CREATE TABLE IF NOT EXISTS Boss (
                                        name TEXT NOT NULL,
                                        deaths INTEGER,
                                        requiredTime INTEGER,
                                        gameTitle TEXT NOT NULL,
                                        PRIMARY KEY (name, gameTitle),
                                        FOREIGN KEY (gameTitle) REFERENCES Game (title)
                                )""")
            self._conn.commit()
        except sqlite3.OperationalError:
            self._notify_observer("Error: A syntax error occured while creating database tables", "error")
    
    
    def _add_game(self, title: str) -> None:
        try:
            self._cursor.execute("""INSERT INTO Game (title)
                                        VALUES (?)""", (title,))
            self._conn.commit()
            
            self._notify_observer(f"The game '{title}' has been added to the save file", None)
        except sqlite3.IntegrityError:
            self._notify_observer(f"Error: The game '{title}' already exists in the save file", "error")
        except sqlite3.OperationalError:
            self._notify_observer(f"Error: A syntax error occured while adding '{title}' to save file", "error")
    
    
    def add_boss(self, boss_name: str, game_title: str) -> None:
        game_exists: bool = self._get_specific_game(game_title)
        
        if not game_exists:
            self._add_game(game_title)
        
        try:
            self._cursor.execute("""INSERT INTO Boss (name, gameTitle)
                                        VALUES (?, ?)""", (boss_name, game_title))
            self._conn.commit()
            
            self._notify_observer(f"The boss '{boss_name}' of game '{game_title}' has been added to the save file", None)
        except sqlite3.IntegrityError:
            if not game_exists:
                self._notify_observer(f"Error: The game '{game_title}' is not added yet", "error")
            else:
                self._notify_observer(f"Error: The boss '{boss_name}' is already added to the game '{game_title}'", "error")
        except sqlite3.OperationalError:
            self._notify_observer(f"Error: A syntax error occured while adding '{game_title}' and '{boss_name}' to save file", "error")
    
    
    def _get_specific_game(self, game_title: str) -> bool:
        self._cursor.execute("""SELECT title FROM Game
                                    WHERE title = (?)""", (game_title,))
        selection: list[str] = self._cursor.fetchone()
        
        if selection is None:
            return False
        else:
            return True
    
    
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
    
    
    def update_boss(self, boss_name: str, game_title: str, deaths: int, required_time: int) -> None:
        self._cursor.execute("""UPDATE Boss
                                    SET deaths = (?), requiredTime = (?)
                                    WHERE name = (?) and gameTitle = (?)""", (deaths, required_time, boss_name, game_title))
        self._conn.commit()
        
        if self._cursor.rowcount == 0:
            self._notify_observer("Nothing was updated because the given value isn't a valid data set in the save file", "error")
        else:
            self._notify_observer(f"The boss '{boss_name}' of game '{game_title}' was updated with the following values: Deaths {deaths}, Req. time {required_time}", None)
    
    
    def get_specific_deaths(self, boss_name: str, game_title: str) -> int:
        self._cursor.execute("""SELECT deaths FROM Boss
                                    WHERE name = (?) and gameTitle = (?)""", (boss_name, game_title))
        tmp_selection: list[int] = self._cursor.fetchall()
        
        for item in tmp_selection:
            selection: int = item[0]
        
        if not tmp_selection:
            self._notify_observer(f"Error: There are no deaths linked to the boss {boss_name} from {game_title} so far", "error")
            return
        else:
            if selection is None:
                return 0
            else:
                return selection
    
    
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
#    
#    
#    def get_specific_statistics(self, boss_name: str) -> list:
#        self.__cursor.execute("""SELECT * FROM Boss
#                                    WHERE name = (?)""", (boss_name,))
#        
#        selection: list = self.__cursor.fetchall()
#        
#        if not selection:
#            print("Nothing was selected because the given value isn't a data set in the database")
#            pass
#        else:
#            return selection
#    
#    
#    def get_all_game_statistics(self) -> list:
#        game_title: str = self.__get_game_title()
#            
#        self.__cursor.execute("""SELECT * FROM Boss b
#                                    JOIN Game g ON b.gameTitle = g.title
#                                    WHERE g.title = (?)""", (game_title,))
#        
#        selection: list = self.__cursor.fetchall()
#        
#        if not selection:
#            print("Nothing was selected because the given value isn't a data set in the database")
#            pass
#        else:
#            return selection
    
    
    def close_connection(self) -> None:
        self._conn.close()