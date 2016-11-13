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

	def tearDown(self):
	   """Tear down"""

	def test_split_cost(self): #not working
	   #rv = self.app.post('/split_cost?Tip=0.2&Billid=364&Total=2.20')
	   # rv = self.app.post('/split_cost', data={'Tip': '0.2', 'Billid': '364', \
	   #  'Total': '2.20'}, follow_redirects=True)
	   rv = self.app.post('/split_cost', data=dict(Tip= '0.2', Billid= '364', Total= '2.20'), follow_redirects=True)
	   assert '2.64' in rv.data

	

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

	def test_login_successful(self):
		rv = self.app.post('/login', data={'email': "test@test", 'password': 'test'}, follow_redirects=True)
		assert 'Bill' in rv.data

	def test_display_bills(self): #not working
		print "testing /bill"
		rv = self.app.get('/bill', data={}, follow_redirects=True)
		assert '364' in rv.data
		assert '365' not in rv.data

	def test_display_bill(self): 
		rv = self.app.post('/display_bill', data={'billId': '364'}, follow_redirects=True)
		assert 'test' in rv.data
		assert 'def' not in rv.data

	def test_add_item_successful(self): #not working
		print "testing /add_item"
		rv = self.app.post('/add_item', data={'billId': '364', 'item': 'aaa', 'quantity': '1', 'price': '1.00'}, follow_redirects=True)
		assert 'aaa' in rv.data

	def test_add_item_invalid_price_quantity(self):
		rv = self.app.post('/add_item', data={'item': 'bbb', 'quantity': '-1', 'price': '0.00'}, follow_redirects=True)
		assert 'bbb' not in rv.data

	def test_remove_item(self): #not working
		print "testing /remove_item"
		rv = self.app.post('/remove_item', data={'ItemName': 'aaa', 'billId': '364'}, follow_redirects=True)
		assert 'aaa' not in rv.data

	def test_add_friend(self): #friend exists


	def test_add_friend(self): #friend doesn't exist


	def test_bill_associated(self): #check if invited friends see their emails associated with billID in bill table


	def test_split_cost_invalid_totalprice(self):


	def test_split_cost_invalid_tip(self):


	def test_users_in_bill(self): #check if bill table only has people associated 


	def test_users_not_in_bill(self): #check if bill table doesn't have people not associated


	def test_login_invalid_email(self):


	def test_signup_invalid_email(self):


	def test_add_item_invalid_item(self):








	#def test_add_item_invalid_name(self):
	#	rv = self.app.post('/add_item', data={'item': '???', 'quantity': '1', 'price': '1.00'}, follow_redirects=True)
	#	assert '???' not in rv.data


if __name__ == '__main__':
	unittest.main()
