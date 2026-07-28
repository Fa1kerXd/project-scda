import sqlite3
from database.connection import main_db



class Logging:
    def __init__(self):
        self.db = main_db()
        self.db.row_factory = sqlite3.Row

    def show_logging(self):
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM logging")
            rows = cursor.fetchall()
            lists = []
            for row in rows:
                lists.append(row['data'])
                lists.append(row['machine'])
                lists.append(row['correction'])
                lists.append(row['coordinator_id'])
                lists.append(row['analyst_id'])
            return lists
        except sqlite3.IntegrityError as e:
            print(f'Erro a integridade da chave estrangeira: {e}')
        except sqlite3.Error as er:
            print(f"Erro no loggin: {er}")
    
    def show_only_logging(self, corrective_patch_id):
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT corrective_patch_id FROM logging WHERE corrective_patch_id = ?", (corrective_patch_id,))
            rows = cursor.fetchall()

            return [row["data"]for row in rows]
        except sqlite3.IntegrityError as e:
            print(f'Erro a integridade da chave estrangeira: {e}')
        except sqlite3.Error as er:
            print(f"Erro no loggin: {er}")

    def log(self, corrective_patch_id):
        try:
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT data, machine, correction, coordinator_id, analyst_id FROM corrective_patch WHERE id = ?",
                (corrective_patch_id,)
            )
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"Correção com id {corrective_patch_id} não encontrada")

            cursor.execute(
                "INSERT INTO logging (corrective_patch_id, data, machine, correction, coordinator_id, analyst_id) VALUES (?, ?, ?, ?, ?, ?)",
                (corrective_patch_id, row["data"], row["machine"], row["correction"], row["coordinator_id"], row["analyst_id"])
            )
            self.db.commit()
        except sqlite3.Error as e:
            print(f'Erro ao salvar Correção no log: {e} - {corrective_patch_id}')
        except ValueError as e:
            print(e)

