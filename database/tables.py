import sqlite3


def create_table_coordinator(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coordinator (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            shift TEXT NOT NULL,
            function TEXT NOT NULL,
            email TEXT NOT NULL)
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f'Error ao criar a tabela: {e}')
        return None


def create_table_analyst(conn):
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyst (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            shift TEXT NOT NULL,
            function TEXT NOT NULL,
            email TEXT NOT NULL)
        """)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao criar tabela analista: {e}")


def create_table_corrective_patch(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS corrective_patch (
            id INTEGER PRIMARY KEY AUTOINCREMENT,     
            data TEXT NOT NULL,
            machine TEXT NOT NULL,
            correction TEXT NOT NULL,
            coordinator_id INTEGER,
            analyst_id INTEGER,
            FOREIGN KEY (coordinator_id) REFERENCES coordinator(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (analyst_id) REFERENCES analyst(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
            )
            """)
        conn.commit()
    except sqlite3.Error as e:
        print(f'Erro ao criar a tabela de Tela Corretiva: {e}')


def create_table_logging(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logging (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            corrective_patch_id INTEGER,
            data TEXT NOT NULL,
            machine TEXT NOT NULL,
            correction TEXT NOT NULL,
            coordinator_id INTEGER,
            analyst_id INTEGER,
            FOREIGN KEY (corrective_patch_id) REFERENCES corrective_patch(id)
                ON DELETE SET NULL
                ON UPDATE CASCADE
            )
            """)
        conn.commit()
    except sqlite3.Error as e:
        print(f'Erro ao criar a tabela logging: {e}')