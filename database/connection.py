import sqlite3
from app_path import DATABASE_FILE

def main_db():

    
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        print("Conectado com sucesso!")
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        print(f'Erro ao criar banco de dados: {e}')
        return conn 


if __name__ == '__main__':
    a = main_db()
    if a is not None:
        b = a.cursor()
        for row in b.execute('select * from coordinator'):
            print(row)
        for woe in b.execute('select * from analyst'):
            print( woe)

        b.close()