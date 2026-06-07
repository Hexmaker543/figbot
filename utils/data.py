import sqlite3, os


database_path = '../.figbot.db'

def get_connection():
    return sqlite3.connect(database_path)

def ensure_database():
    os.makedirs(name=database_path, exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()
    with open('create_database.sql', 'r') as sql_file:
        sql_script = sql_file.read()
        cursor.executescript(sql_script)
    conn.commit()
    conn.close()
