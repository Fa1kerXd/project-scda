import sqlite3
from database.connection import main_db


class UserBase:
    TABLE_NAME = None  # subclasses definem: "analyst" ou "coordinator"

    def __init__(self, name, shift, function, email):
        self._name = name
        self._shift = shift
        self._user_function = function
        self.email = email

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def shift(self):
        return self._shift

    @shift.setter
    def shift(self, value):
        self._shift = value

    @property
    def user_function(self):
        return self._user_function

    @user_function.setter
    def user_function(self, value):
        self._user_function = value

    def pk(self):
        conn = main_db()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT id FROM {self.TABLE_NAME} WHERE name=?", (self._name,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"{self.TABLE_NAME} '{self._name}' não encontrado no banco")
            return row[0]
        finally:
            conn.close()

    def get_email(self):
        conn = main_db()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT email FROM {self.TABLE_NAME} WHERE name=?", (self._name,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"{self.TABLE_NAME} '{self._name}' não encontrado no banco")
            return row[0]
        finally:
            conn.close()

    def id_from_name(self, record_id):
        conn = main_db()
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT name FROM {self.TABLE_NAME} WHERE id=?", (record_id,))
            row = cursor.fetchone()
            if row is None:
                raise ValueError(f"{self.TABLE_NAME} com id {record_id} não encontrado")
            return row[0]
        finally:
            conn.close()

    def show_all(self):
        conn = main_db()
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {self.TABLE_NAME}")
            return [row['name'] for row in cursor.fetchall()]
        finally:
            conn.close()