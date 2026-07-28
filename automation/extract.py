import sqlite3
import sys
from pathlib import Path
# from models.logging import coordinator_aline, analyst_augusto
from models.user_high_position import Coordinator
from models.user_analyst import Analyst
from database.connection import main_db
from app_path import EMAIL_ATTACHMENT_FILE
db = main_db()

def context_manager(filename, body, coordinator: Coordinator, analyst: Analyst):
    with open(filename, 'w', encoding='utf-8') as file:
        for index,line in enumerate(body):
            corrective_id = line[0]
            data = line[1]
            machine = line[2]
            corrective = line[3]
            coordinator_id = line[4]
            analyst_id = line[5]

            file.write(f"""
            Data: {str(data)}
            Maquina: {str(machine)}
            Correção: {str(corrective)}
            Coordenador: {coordinator.id_from_name(coordinator_id)}
            Analista: {analyst.id_from_name(analyst_id)}

            """)
            print('ok')
def extract_content(coordinator: Coordinator, analyst: Analyst, filename=EMAIL_ATTACHMENT_FILE):
    try:
        cursor = db.cursor()
        cursor.execute(
            'SELECT * FROM corrective_patch WHERE coordinator_id=?'
        ,(coordinator.pk(),))
        content = cursor.fetchall()
        context_manager(filename, content, coordinator, analyst)
    except sqlite3.Error as e:
        print(f'Erro ao extrair conteúdo: {e}')

# if __name__ == "__main__":
#     cursor = db.cursor()
#     cursor.execute(
#         'SELECT * FROM corrective_patch'
#     )
#     content = cursor.fetchall()

#     context_manager(FILE, content,  coordinator_aline, analyst_augusto)