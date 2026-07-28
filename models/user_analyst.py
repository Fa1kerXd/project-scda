from database.create_user import create_analyst
from database.connection import main_db
from .user_base import UserBase


class Analyst(UserBase):
    TABLE_NAME = "analyst"

    def conn(self):
        create_analyst(self._name, self._shift, self._user_function, self.email, main_db())