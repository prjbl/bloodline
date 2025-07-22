import sqlite3
from directory import Directory

class Statistics:
    
    __file_name: str = "statistics.db"
    __dir: Directory = Directory()
    
    __conn: sqlite3.Connection = sqlite3.connect(__dir.get_persistent_data_path().joinpath(__file_name))
    __cursor: sqlite3.Cursor = __conn.cursor()
    
    
    def __init__(self):
        self.__create_table(self.__cursor)

    
    def __create_table(self, cursor=__cursor) -> None:
        cursor.execute("""CREATE TABLE IF NOT EXISTS Boss (
                            name TEXT PRIMARY KEY,
                            deaths INTEGER
                            requiredTime TEXT
                            )""")
    
    
    def set_boss_name(self, boss_name: str) -> None:
        try:
            self.__cursor.execute("""INSERT INTO Boss (name)
                                        VALUES (?)""", (boss_name,))
        except sqlite3.IntegrityError:
            print("An error occured: value is already exists in the database")
    
    
    def set_specific_statistics(self, boss_name: str, deaths: int, requiredTime: str) -> None:
        self.__cursor.execute("""UPDATE Boss
                                    SET deaths = (?), requiredTime = (?)
                                    WHERE name = (?)""", (deaths, requiredTime, boss_name))
        self.__conn.commit()
    
    
    def get_specific_statistics(self, boss_name: str) -> list:
        self.__cursor.execute("""SELECT * FROM Boss
                                    WHERE name = (?)""", (boss_name,))
        return self.__cursor.fetchall()
    
    
    def get_all_statistics(self) -> list:
        self.__cursor.execute("""SELECT * FROM Boss""")
        return self.__cursor.fetchall()
    
    
    def close_db_connection(self) -> None:
        self.__conn.close()