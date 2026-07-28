import sqlite3
from database.connection import main_db
db = main_db()
def extract_corrective_patch():
    try:
        cursor = db.cursor()
        cursor.execute(
            'SELECT * FROM corrective_patch'
        )
        content = cursor.fetchall()
        print(content)
    except sqlite3.Error as e:
        raise e 

