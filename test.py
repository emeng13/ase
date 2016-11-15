"""app unit tests"""
# reference: http://www.drdobbs.com/testing/unit-testing-with-python/240165163
import pymssql 
import os
import unittest

from app import app 

from mock import patch

test_user = "test@test1"

conn = pymssql.connect(server='eats.database.windows.net', \
	user='th2520@eats',\
	password='123*&$eats',\
	database='AERIS')\

class MyTest(unittest.TestCase):
	def setUp(self):
		 """Set up"""
		 self.app = app.test_client(self)
		 self.conn = pymssql.connect(server='eats.database.windows.net', \
			user='th2520@eats',\
			password='123*&$eats',\
			database='AERIS')\
		

	def tearDown(self):
		 """Tear down"""
		 conn = self.conn
		 cursor = conn.cursor()
		 cursor.execute("DELETE FROM Bill_Users WHERE billID=%d AND Email=%s", (221, "tin@test.com"))
		 cursor.execute("DELETE FROM Users WHERE Email=%s", 'test1@test')
		 conn.commit()
		 self.conn.close()
		 # remove test_user (global var)
		 # remove bill (don't know if this is possible since we use random numbers when we create the bill)
		 # remove test_user from bill 221

	@patch('app.bill_id', 364)
	def test_split_cost(self): #not working
		"""Successful split cost"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'
		rv = self.app.post('/split_cost', data={'Tip':'0.2', 'Total': '2.20'}, follow_redirects=True)
		assert '2.64' in rv.data

		rv = self.app.post('/split_cost', data={'Tip':'0.2', 'Total': '7.20'}, follow_redirects=True)
		assert '8.64' in rv.data


	def test_login_user_not_exist(self):
		"""Login where user doesn't exist"""
		rv = self.app.post('/login', data={'email': "not_test@test", 'password': 'test'}, follow_redirects=True)
		assert 'Sign up first' in rv.data

	def test_login_incorrect_password(self):
		"""Login where password is wrong"""
		rv = self.app.post('/login', data={'email': "test@test", 'password': 'not_test'}, follow_redirects=True)
		assert 'Incorrect password' in rv.data

	def test_signup_successful(self):
		"""Successful creating account"""
		global test_user
		rv = self.app.post('/signUp', data={'firstName': 'Test', 'lastName': 'Test', 'email': test_user, \
			'password': 'test'}, follow_redirects=True)
		assert 'Your account is registered successfully!' in rv.data

	def test_signup_same_user(self):
		"""Create account that exists already"""
		rv = self.app.post('/signUp', data={'firstName': 'Test', 'lastName': 'Test', 'email': "test@test", \
			'password': 'test'}, follow_redirects=True)		
		assert 'You registered with the same email before.' in rv.data

	def test_login_successful(self):
		"""Successful login"""
		rv = self.app.post('/login', data={'email': "test@test", 'password': 'test'}, follow_redirects=True)
		assert 'Bill' in rv.data

	def test_create_bill(self):
		"""Create bill"""
		#how
		
	def test_display_bills(self): 
		"""Check bill IDs displayed are correct"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'
		
		rv = self.app.get('/bill', data={}, follow_redirects=True)
		assert '364' in rv.data
		assert '365' not in rv.data

	def test_display_bill_items(self): 
		"""Check items displayed are correct"""
		rv = self.app.post('/display_bill', data={'billId': '221'}, follow_redirects=True)
		assert 'test' in rv.data
		assert 'def' not in rv.data

	def test_display_bill_people(self): 
		"""Check people associated with bill are correct"""
		rv = self.app.post('/display_bill', data={'billId': '221'}, follow_redirects=True)
		assert 'test@test' in rv.data
		assert 'hello' not in rv.data

	@patch('app.bill_id', 221)
	def test_add_item_successful(self): 
		"""Check item added successfully"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'

		# with patch('self.app.bill_id', 364):
		rv = self.app.post('/add_item', data={'item': 'chicken', 'quantity': '1', 'price': '7.00'}, follow_redirects=True)
		assert 'chicken' in rv.data

	@patch('app.bill_id', 221)
	def test_add_item_invalid_price_quantity(self):
		"""Add item with invalid input values"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'

		rv = self.app.post('/add_item', data={'item': 'bbb', 'quantity': '-1', 'price': '0.00'}, follow_redirects=True)
		assert 'INVALID INPUT VALUES (Price and Quantity have to be positive values, Item Name can only include alphanumeric characters)' in rv.data
		assert 'bbb' not in rv.data

	def test_remove_item(self): 
		"""Successful removing item"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'
		rv = self.app.post('/remove_item', data={'ItemName': 'chicken'}, follow_redirects=True)
		assert 'chicken' not in rv.data

	def test_add_friend_not_exist(self): 
		"""Add user to bill -- user doesn't exist"""
		rv = self.app.post('/add_friend', data= {'Friend_email': 'random@email.com', 'Billid': '221'}, follow_redirects=True)
		assert 'NO ACCOUNT WITH THIS EMAIL EXISTS' in rv.data

	@patch('app.bill_id', 221)
	def test_add_friend_successful(self): 
		"""Successful adding friend to bill"""
		global test_user
		rv = self.app.post('/add_friend', data={'Friend_email': test_user, 'Billid': '221'}, follow_redirects=True)
		assert test_user in rv.data

	def test_add_friend_same_email(self): 
		"""Add user to bill twice"""
		global test_user
		rv = self.app.post('/add_friend', data={'Friend_email': test_user, 'Billid': '221'}, follow_redirects=True)
		assert "THIS EMAIL WAS ALREADY IN THE BILL." in rv.data

	def test_split_cost_invalid_totalprice(self):
		"""Split cost with invalid total cost input"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'
		rv = self.app.post('/split_cost', data={'Tip': '0.0', 'Total': '-1'}, follow_redirects=True)
		assert "TIP AND POST TAX COST HAVE TO BE POSITIVE VALUES" in rv.data

	def test_split_cost_invalid_tip(self):
		"""Split cost with invalid tip input"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'
		rv = self.app.post('/split_cost', data={'Tip': '-0.4', 'Total': '100'}, follow_redirects=True)
		assert "NUMERICAL INPUTS ONLY" in rv.data

	def test_login_invalid_email(self):
		"""Login with invalid email"""
		rv = self.app.post('/login', data={'email': "test", 'password': 'test'}, follow_redirects=True)
		assert 'Invalid email!' in rv.data
		assert 'test' not in rv.data

	def test_signup_invalid_email(self):
		"""Sign up with invalid email"""
		rv = self.app.post('/signUp', data={'firstName': 'Test', 'lastName': 'Test', 'email': "random", \
			'password': 'test'}, follow_redirects=True)
		assert 'Invalid email!' in rv.data
		assert 'random' not in rv.data

	@patch('app.bill_id', 221)
	def test_add_item_invalid_item(self):
		"""Add item with invalid name"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'
			
		rv = self.app.post('/add_item', data={'item': '???', 'quantity': '1', 'price': '1.00'}, follow_redirects=True)
		assert 'INVALID INPUT VALUES (Price and Quantity have to be positive values, Item Name can only include alphanumeric characters)' in rv.data
		assert '???' not in rv.data


if __name__ == '__main__':
	unittest.main()
