import unittest 
from models.user_high_position import Coordinator


class UserHighPositionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.user = Coordinator(name='default',shift='A')
        return super().setUp()
    
    def test_coordinator_turn_is_functional(self):
        self.user.shift = 'A'
        self.assertEqual('A', self.user.shift)

    def test_coordinator_name_is_correct(self):
        self.user._name = 'Eduardo'
        self.assertEqual('Eduardo', self.user._name)