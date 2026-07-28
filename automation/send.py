import sqlite3
from .email import send_email
from models.user_high_position import Coordinator

def save(coordinator: Coordinator, to_email, from_email, password, subject, body, db: sqlite3.Connection,send_email_true = False):
    if send_email_true:
        send_email(to_email, from_email, subject, password, body, send_email_true)
        send_email_true = False
    pk = coordinator.pk()
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO logging (coordinator_id) VALUES (?)", (pk))
        db.commit()
    except sqlite3.IntegrityError as e:
        print(f"Erro na integridade da chave estrangeira: {e}")
