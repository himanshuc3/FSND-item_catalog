import unittest
from app.main.database_setup import User

class UserModelTestCase(unittest.TestCase):
    # Checking whether password setter is working correctly
    def test_password_setter(self):
        u = User(name='Rahul', email='generic@email.com', password='cat')
        self.assertTrue(u.password_hash is not None)

    #Test whether fetching password raise Error
    def test_no_password_getter(self):
        u = User(name='Rahul', email='generic@email.com', password='cat')
        with self.assertRaises(AttributeError):
            u.password

    #Testing whether verify password is working
    def test_password_verification(self):
        u = User(name='Rahul', email='generic@email.com', password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)
