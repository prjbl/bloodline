import sqlite3
from directory import Directory

file_name: str = "statistics.db"
#connection: sqlite3 = sqlite3.connect(Directory.get_file_path() + file_name)
connection: sqlite3.Connection = sqlite3.connect(file_name)
cursor: sqlite3.Cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS Boss (
                    name TEXT PRIMARY KEY,
                    deaths INTEGER,
                    requiredTime TEXT
                    )""")


def set_boss_name(boss_name: str) -> None:
    try:
        cursor.execute("""INSERT INTO Boss (name)
                            VALUES (?)""", (boss_name,))
        connection.commit()
    except sqlite3.IntegrityError:
        print("An error occured: value is already exists in the database")


def set_specific_statistics(boss_name: str, deaths: int, requiredTime: str) -> None:
    cursor.execute("""UPDATE Boss
                        SET deaths = (?), requiredTime = (?)
                        WHERE name = (?)""", (deaths, requiredTime, boss_name))
    connection.commit()


def get_specific_statistics(boss_name: str) -> list:
    cursor.execute("""SELECT * FROM Boss
                        WHERE name = (?)""", (boss_name,))
    return cursor.fetchall()


def get_all_statistics() -> list:
    cursor.execute("""SELECT * FROM Boss""")
    return cursor.fetchall()


def close_db_connection() -> None:
    connection.close()
    
#test values below
#set_boss_name("Malenia")
#set_boss_name("Maliketh the black Blade")
#set_specific_statistics("Maliketh the black Blade", 53, "2h")
print(get_specific_statistics("Malenia"))
print(get_all_statistics())