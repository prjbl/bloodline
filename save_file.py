import sqlite3
from directory import Directory

class SaveFile:
    
    __file_name: str = "save_file.db"
    __dir: Directory = Directory()
    
    __conn: sqlite3.Connection = sqlite3.connect(__dir.get_persistent_data_path().joinpath(__file_name))
    __cursor: sqlite3.Cursor = __conn.cursor()
    
    
    def __init__(self):
        self.__create_tables(self.__cursor, self.__conn)

    
    def __create_tables(self, cursor=__cursor, conn=__conn) -> None:
        try:
            cursor.execute("""CREATE TABLE IF NOT EXISTS Game (
                                title TEXT NOT NULL,
                                PRIMARY KEY (title)
                            )""")
            
            cursor.execute("""CREATE TABLE IF NOT EXISTS Boss (
                                name TEXT NOT NULL,
                                deaths INTEGER,
                                requiredTime TEXT,
                                gameTitle TEXT NOT NULL,
                                PRIMARY KEY (name),
                                FOREIGN KEY (gameTitle) REFERENCES Game (title)
                            )""")
            conn.commit()
        except sqlite3.OperationalError as e:
            print(f"An error occured: {e}")
    
    
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
        self.__conn.close()