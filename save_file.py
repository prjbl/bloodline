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
                                        requiredTime TEXT,
                                        gameTitle TEXT NOT NULL,
                                        PRIMARY KEY (name),
                                        FOREIGN KEY (gameTitle) REFERENCES Game (title)
                                )""")
            self._conn.commit()
        except sqlite3.OperationalError:
            self._notify_observer("Error: A syntax error occured while creating database tables", "error")
    
    
    def add_game_title(self, title: str) -> None:
        try:
            self._cursor.execute("""INSERT INTO Game (title)
                                        VALUES (?)""", (title,))
            self._conn.commit()
            
            self._notify_observer(f"The game '{title}' has been added to the save file", None)
        except sqlite3.IntegrityError:
            self._notify_observer(f"Error: The game '{title}' already exists in the save file", "error")
        except sqlite3.OperationalError:
            self._notify_observer(f"Error: A syntax error occured while adding '{title}' to save file", "error")
    
    
    def add_boss_name(self, boss: str, game: str) -> None:
        boss = "Hund"
        game = "Hund Game"
        game_exists: bool = self._get_specific_game(game)
        
        if not game_exists:
            self.add_game_title(game)
        
        try:
            self._cursor.execute("""INSERT INTO Boss (name, gameTitle)
                                        VALUES (?, ?)""", (boss, game))
            self._conn.commit()
            
            self._notify_observer(f"The boss '{boss}' of game '{game}' has been added to the save file", None)
        except sqlite3.IntegrityError:
            if not game_exists:
                self._notify_observer(f"Error: The game '{game}' is not added yet", "error")
            else:
                self._notify_observer(f"Error: The boss '{boss}' already exists in the save file", "error")
        except sqlite3.OperationalError:
            self._notify_observer(f"Error: A syntax error occured while adding '{game}' and '{boss}' to save file", "error")
    
#    def add_boss_name(self, name: str) -> None:
#        try:
#            game_title: str = "Schwanz"
#            
#            self._cursor.execute("""INSERT INTO Boss (name, gameTitle)
#                                        VALUES (?, ?)""", (name, game_title))
#            self._conn.commit()
#            
#            self._notify_observer(f"The boss '{name}' has been added to the save file", None)
#        except sqlite3.IntegrityError:
#            self._notify_observer(f"Error: The boss '{name}' already exists in the save file", "error") #or game title is not in db
#        except sqlite3.OperationalError:
#            self._notify_observer(f"Error: A syntax error occured while adding '{name}' to save file", "error")
    
    
    def get_all_games(self) -> list[str]:
        self._cursor.execute("""SELECT * FROM Game""")
        
        selection: list[str] = self._cursor.fetchall()
        
        if not selection:
            self._notify_observer(f"Error: There are no games in the save file so far", "error")
            return []
        else:
            cleaned_selection: list[str] = []
            
            for item_tuple in selection:
                    cleaned_selection.extend(item_tuple)
            
            return cleaned_selection
    
    
    def _get_specific_game(self, game: str) -> bool:
        self._cursor.execute("""SELECT title FROM Game
                                    WHERE title = (?)""", (game,))
        selection: str = self._cursor.fetchone()
        
        if game == selection:
            return True
        else:
            return False
    
    
#    def update_specific_statistics(self, boss_name: str, deaths: int, requiredTime: str) -> None:
#        self.__cursor.execute("""UPDATE Boss
#                                    SET deaths = (?), requiredTime = (?)
#                                    WHERE name = (?)""", (deaths, requiredTime, boss_name))
#        self.__conn.commit()
#        
#        if self.__cursor.rowcount == 0:
#            print("Nothing was updates because the given value isn't a data set in the database")
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