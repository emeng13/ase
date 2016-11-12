"""app unit tests"""
# reference: http://www.drdobbs.com/testing/unit-testing-with-python/240165163
import pymssql 
import os
import unittest

from app import app

user_email = "test@test"
bill_id = -1

conn = pymssql.connect(server='eats.database.windows.net', \
  user='th2520@eats',\
  password='123*&$eats',\
  database='AERIS')\

class MyTest(unittest.TestCase):
	"""Test class"""
	def setUp(self):
	   """Set up"""
	   self.app = app.test_client(self)
	   print("in setUp")

	def tearDown(self):
	   """Tear down"""

	def test_split_cost(self):
	   #rv = self.app.post('/split_cost?Tip=0.2&Billid=364&Total=2.20')
	   # rv = self.app.post('/split_cost', data={'Tip': '0.2', 'Billid': '364', \
	   #  'Total': '2.20'}, follow_redirects=True)
	   rv = self.app.post('/split_cost', data=dict(Tip= '0.2', Billid= '364', Total= '2.20'), follow_redirects=True)
	   assert '2.64' in rv.data

	def test_login_successful(self):
		rv = self.app.post('/login', data={'email': "test@test", 'password': 'test'}, follow_redirects=True)
		assert 'Bill' in rv.data

	def test_login_user_not_exist(self):
		rv = self.app.post('/login', data={'email': "not_test@test", 'password': 'test'}, follow_redirects=True)
		assert 'Sign up first' in rv.data

	def test_login_incorrect_password(self):
		rv = self.app.post('/login', data={'email': "test@test", 'password': 'not_test'}, follow_redirects=True)
		assert 'Incorrect password' in rv.data

	def test_signup_successful(self):
		rv = self.app.post('/signUp', data={'firstName': 'Test', 'lastName': 'Test', 'email': "test1@test", \
			'password': 'test'}, follow_redirects=True)
		assert 'Your account is registered successfully!' in rv.data

	def test_signup_same_user(self):
		rv = self.app.post('/signUp', data={'firstName': 'Test', 'lastName': 'Test', 'email': "test@test", \
			'password': 'test'}, follow_redirects=True)		
		assert 'You registered with the same email before.' in rv.data



if __name__ == '__main__':
	unittest.main()
