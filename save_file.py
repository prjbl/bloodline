import sqlite3
from directory import dir

class SaveFile:
    
    def __init__(self):
        self._conn: sqlite3.Connection = sqlite3.connect(dir.get_persistent_data_path().joinpath(self._FILE_NAME))
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
        except sqlite3.OperationalError as e:
            self._notify_observer("Error: A syntax error occured while creating database tables", "error")
    
    
    def add_game_title(self, title: str) -> None:
        try:
            self.__cursor.execute("""INSERT INTO Game (title)
                                        VALUES (?)""", (title,))
            self.__conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"An error occured: {e}")
        except sqlite3.OperationalError as e:
            print(f"An error occured: {e}")
    
    
    def add_boss_name(self, name: str) -> None:
        try:
            game_title: str = self.__get_game_title()
            
            self.__cursor.execute("""INSERT INTO Boss (name, gameTitle)
                                        VALUES (?, ?)""", (name, game_title))
            self.__conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"An error occured: {e}") # value alreade exists in db
        except sqlite3.OperationalError as e:
            print(f"An error occured: {e}")
    
    
    def select_game_title(self) -> None:
        pass
    
    
    def __get_game_title(self) -> str:
        pass
    
    
    def update_specific_statistics(self, boss_name: str, deaths: int, requiredTime: str) -> None:
        self.__cursor.execute("""UPDATE Boss
                                    SET deaths = (?), requiredTime = (?)
                                    WHERE name = (?)""", (deaths, requiredTime, boss_name))
        self.__conn.commit()
        
        if self.__cursor.rowcount == 0:
            print("Nothing was updates because the given value isn't a data set in the database")
    
    
    def get_specific_statistics(self, boss_name: str) -> list:
        self.__cursor.execute("""SELECT * FROM Boss
                                    WHERE name = (?)""", (boss_name,))
        
        selection: list = self.__cursor.fetchall()
        
        if not selection:
            print("Nothing was selected because the given value isn't a data set in the database")
            pass
        else:
            return selection
    
    
    def get_all_game_statistics(self) -> list:
        game_title: str = self.__get_game_title()
            
        self.__cursor.execute("""SELECT * FROM Boss b
                                    JOIN Game g ON b.gameTitle = g.title
                                    WHERE g.title = (?)""", (game_title,))
        
        selection: list = self.__cursor.fetchall()
        
        if not selection:
            print("Nothing was selected because the given value isn't a data set in the database")
            pass
        else:
            return selection
    
    
    def close_connection(self) -> None:
        self._conn.close()