import sqlite3


def create_coordinator(name, shift, function, email ,db: sqlite3.Connection):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO coordinator (name, shift, function, email) VALUES (?, ?, ?, ?)", 
            (name, shift, function, email))
        db.commit()
        print('Coordenador Criado com sucesso!')
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f'Erro ao criar um usuario: {e}')


def create_analyst(name, shift, function, email, db: sqlite3.Connection):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO analyst (name, shift, function, email) VALUES (?, ?, ?, ?)", 
            (name, shift, function, email))
        db.commit()
        print('Analista Criado com sucesso!')
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f'Erro ao criar um usuario analista: {e}')


def create_corrective_patch(data, machine, correction, coordinator_id, analyst_id, db: sqlite3.Connection ):
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO corrective_patch (data, machine, correction, coordinator_id, analyst_id) VALUES (?, ?, ?, ?, ?)",
            (data, machine, correction, coordinator_id, analyst_id)           
            )
        db.commit()
    except sqlite3.IntegrityError as e:
        print(f"Erro de integridade com cahve estrangeira: {e}")


