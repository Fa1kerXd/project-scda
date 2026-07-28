from database.create_user import create_coordinator
from database.connection import main_db
from .user_base import UserBase


class Coordinator(UserBase):
    TABLE_NAME = "coordinator"

    def conn(self):
        create_coordinator(self._name, self._shift, self._user_function, self.email, main_db())