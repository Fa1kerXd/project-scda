import unittest
import sqlite3
from database.connection import main_db
from database.create_user import create_analyst, create_corrective_patch, create_coordinator
from database.tables import create_table_coordinator, create_table_analyst, create_table_corrective_patch, create_table_logging
from models.logging import Logging
from models.user_analyst import Analyst
class AnalystDatabaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.db = main_db()
        create_table_coordinator(self.db)
        create_table_analyst(self.db)
        create_table_corrective_patch(self.db)
        create_table_logging(self.db)
        self.user = Analyst('Augusto', 'Central')
        self.user.conn()
        self.name_user = self.user._name
        self.analyst = create_analyst('Augusto', 'Central', 'Analista', self.db)
        self.coordinator = create_coordinator('Eduardo', 'B', 'Coordenador', self.db)
        self.corrective_id = create_corrective_patch(
            '2026-07-30',
            'Fabrima 5',
            'Corrigir apontamento na fabrima 5',
            self.coordinator,
            self.analyst,
            self.db,
        )
        self.logger = Logging()
        self.logger.log(self.corrective_id)
        return super().setUp()

    def test_the_test(self):
        machine = 'Fabrima 5'
        result = self.logger.show_logging()
        self.assertEqual(machine, result['machine'])
    
    def test_if_name_is_unique(self):
        
        with self.assertRaises(sqlite3.OperationalError):
            new = Analyst('Augusto', 'Central')
            new.conn()
            msg = "UNIQUE constraint failed: analyst.name"
            
            self.assertEqual(new._name, self.name_user)