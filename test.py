"""app unit tests"""
# reference: http://www.drdobbs.com/testing/unit-testing-with-python/240165163
import pymssql 
import os
import unittest

from app import app 

from mock import patch

test_user1 = "test@test1"
test_user2 = "test@test2"

conn = pymssql.connect(server='eats.database.windows.net', \
	user='th2520@eats',\
	password='123*&$eats',\
	database='AERIS')\

class MyTest(unittest.TestCase):
	def setUp(self):
		 """Set up"""


		 global test_user1
		 global test_user2
		 self.app = app.test_client(self)
		 self.conn = pymssql.connect(server='eats.database.windows.net', \
			user='th2520@eats',\
			password='123*&$eats',\
			database='AERIS')

		 conn = self.conn
		 cursor = conn.cursor()
		 cursor.execute("SELECT * FROM Users WHERE Email=%s", test_user2)
		 if cursor.rowcount == 0:
		 		cursor.execute("INSERT INTO Users VALUES (%s, %s, %s, %s)", ("test","test", test_user2, "test"))
		 self.conn.commit()

		 cursor.execute("SELECT * FROM Users WHERE Email=%s", test_user1)
		 if cursor.rowcount != 0:
		  	cursor.execute("DELETE FROM Users WHERE Email=%s", (test_user1))
		  	self.conn.commit()
		 cursor.close()


	def tearDown(self):
		 """Tear down"""
		 

		 global test_user2
		 conn = self.conn
		 cursor = conn.cursor()	
		 
		 cursor.execute("DELETE FROM Bill_Users WHERE Email=%s AND billID=%d", (test_user2, 182))

		 self.conn.commit()
		 self.conn.close()

	
	def test_login_user_not_exist(self):
		"""Login where user doesn't exist"""
		rv = self.app.post('/login', data={'email': "not_test@test", 'password': 'test'}, follow_redirects=True)
		assert 'Sign up first' in rv.data
		print "test_login_user_not_exist passes!"

	def test_login_incorrect_password(self):
		"""Login where password is wrong"""
		rv = self.app.post('/login', data={'email': "test@test", 'password': 'not_test'}, follow_redirects=True)
		assert 'Incorrect password' in rv.data
		print "test_login_incorrect_password passes!"

	def test_signup_successful(self):
		"""Successful creating account"""
		global test_user1
		rv = self.app.post('/signUp', data={'firstName': 'Test', 'lastName': 'Test', 'email': test_user1, \
			'password': 'test'}, follow_redirects=True)
		assert 'Your account is registered successfully!' in rv.data
		print "test_signup_successful passes!"

	def test_signup_same_user(self):
		"""Create account that exists already"""
		rv = self.app.post('/signUp', data={'firstName': 'Test', 'lastName': 'Test', 'email': "test@test", \
			'password': 'test'}, follow_redirects=True)		
		assert 'You registered with the same email before.' in rv.data
		print "test_signup_same_user passes!"

	def test_login_successful(self):
		"""Successful login"""
		rv = self.app.post('/login', data={'email': "test@test", 'password': 'test'}, follow_redirects=True)
		assert 'Bill' in rv.data
		print "test_login_successful passes!"

	def test_create_bill(self):
		"""Create bill"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'


		rv = self.app.post('/create_bill', data={}, follow_redirects=True)
		assert 'is created!' in rv.data
		print "test_create_bill passes!"
		
	def test_display_bills(self): 
		"""Check bill IDs displayed are correct"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'
		
		rv = self.app.get('/bill', data={}, follow_redirects=True)
		assert '182' in rv.data
		print "test_display_bill passes!"

	def test_display_bill_items(self): 
		"""Check items displayed are correct"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'

		rv = self.app.post('/display_bill', data={'billId': '182'}, follow_redirects=True)
		assert 'test@test' in rv.data
		assert 'def' not in rv.data
		print "test_display_bill_items passes!"

	def test_display_bill_people(self): 
		"""Check people associated with bill are correct"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'

		rv = self.app.post('/display_bill', data={'billId': '182'}, follow_redirects=True)
		assert 'test@test' in rv.data
		assert 'hello' not in rv.data
		print "test_display_bill_people passes!"

	@patch('app.bill_id', 182)
	def test_add_item_successful(self): 
		"""Check item added successfully"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'

		rv = self.app.post('/add_item', data={'item': 'chicken', 'quantity': '1', 'price': '7.00'}, follow_redirects=True)
		assert 'chicken' in rv.data
		print "test_add_item_successful passes!"

	def test_remove_item(self): 
		"""Successful removing item"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'
		rv = self.app.post('/remove_item', data={'ItemName': 'chicken'}, follow_redirects=True)
		assert 'chicken' not in rv.data
		print "test_remove_item passes!"

	@patch('app.bill_id', 182)
	def test_add_item_invalid_price_quantity(self):
		"""Add item with invalid input values"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'

		rv = self.app.post('/add_item', data={'item': 'bbb', 'quantity': '-1', 'price': '0.00'}, follow_redirects=True)
		assert 'INVALID INPUT VALUES (Price and Quantity have to be positive values, Item Name can only include alphanumeric characters)' in rv.data
		assert 'bbb' not in rv.data
		print "test_add_item_invalid_price_quantity passes!"

	def test_add_friend_not_exist(self): 
		"""Add user to bill -- user doesn't exist"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'

		rv = self.app.post('/add_friend', data= {'Friend_email': 'random@email.com', 'Billid': '182'}, follow_redirects=True)
		assert 'NO ACCOUNT WITH THIS EMAIL EXISTS' in rv.data
		print "test_add_friend_not_exist passes!"

	@patch('app.bill_id', 182)
	def test_add_friend_successful(self): 
		"""Successful adding friend to bill"""
		global test_user2

		with self.app.session_transaction() as sess:
			sess['username']='test@test'

		rv = self.app.post('/add_friend', data={'Friend_email': test_user2, 'Billid': '182'}, follow_redirects=True)
		assert test_user2 in rv.data
		print "test_add_friend_successful passes!"

	def test_add_friend_same_email(self): 
		"""Add user to bill twice"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'
			
		rv = self.app.post('/add_friend', data={'Friend_email': "test@test", 'Billid': '182'}, follow_redirects=True)
		assert "THIS EMAIL WAS ALREADY IN THE BILL." in rv.data
		print "test_add_friend_same_email passes!"

	@patch('app.bill_id', 182)
	def test_split_cost(self): 
		"""Successful split cost"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'
			
		rv = self.app.post('/split_cost', data={'Tip':'0.10', 'Total': '18'}, follow_redirects=True)
		assert '12.10' in rv.data
		print "test_split_cost passes!"

	@patch('app.bill_id', 182)
	def test_split_cost_invalid_totalprice(self):
		"""Split cost with invalid total cost input"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'
		rv = self.app.post('/split_cost', data={'Tip': '0.0', 'Total': '-1'}, follow_redirects=True)
		assert "TIP AND POST TAX COST HAVE TO BE POSITIVE VALUES" in rv.data
		print "test_split_cost_invalid_totalprice passes!"

	@patch('app.bill_id', 182)
	def test_split_cost_invalid_tip(self):
		"""Split cost with invalid tip input"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'
		rv = self.app.post('/split_cost', data={'Tip': '-0.4', 'Total': '100'}, follow_redirects=True)
		assert "NUMERICAL INPUTS ONLY" in rv.data
		print "test_split_cost_invalid_tip passes!"



	@patch('app.bill_id', 182)
	def test_add_item_invalid_item(self):
		"""Add item with invalid name"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'
			
		rv = self.app.post('/add_item', data={'item': '???', 'quantity': '1', 'price': '1.00'}, follow_redirects=True)
		assert 'INVALID INPUT VALUES (Price and Quantity have to be positive values, Item Name can only include alphanumeric characters)' in rv.data
		assert '???' not in rv.data
		print "second iteration test"
		print "test_add_item_invalid_item passes!"


	@patch('app.bill_id', 182)
	def test_edit_item_invalid_price_quantity(self):
		"""Edit item with invalid input values"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'

		self.app.post('/add_item', data={'item': 'aaa', 'quantity': '1', 'price': '7.00'}, follow_redirects=True)
		rv = self.app.post('/edit_item', data={'ItemName': 'aaa', 'quantity': '-1', 'price': '0.00'}, follow_redirects=True)
		assert 'INVALID INPUT VALUES (Price and Quantity have to be positive values)' in rv.data
		self.app.post('/remove_item', data={'ItemName': 'aaa'}, follow_redirects=True)
		print "second iteration test"
		print "test_edit_item_invalid_price_quantity passes!"

	@patch('app.bill_id', 182)
	def test_edit_item_successful(self):
		"""Edit item with invalid input values"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test'

		self.app.post('/add_item', data={'item': 'bbb', 'quantity': '1', 'price': '7.00'}, follow_redirects=True)
		rv = self.app.post('/edit_item', data={'ItemName': 'bbb', 'quantity': '100', 'price': '7.00'}, follow_redirects=True)
		assert '100' in rv.data
		self.app.post('/remove_item', data={'ItemName': 'bbb'}, follow_redirects=True)
		print "second iteration test"
		print "test_edit_item_successful passes!"

	def test_forgot_password_unregisteredEmail(self):
		"""Do Forgot Password? with unregistered email"""
		rv = self.app.post('/checkEmail', data={'email': 'random@email.com'}, follow_redirects=True)
		assert 'There is no account with this email address.' in rv.data
		assert 'random@email.com' not in rv.data
		print "second iteration test"
		print "test_forgot_password_unregisteredEmail passes!"

	def test_forgot_password_registeredEmail(self):
		"""Do Forgot Password? with registered email"""
		rv = self.app.post('/checkEmail', data={'email': 'test@test'}, follow_redirects=True)
		assert "test@test" in rv.data
		print "second iteration test"
		print "test_forgot_password_registeredEmail passes!"

	def test_change_password(self):
		"""Successful change of password"""
		global test_user2
		rv = self.app.post('/changePassword', data={'email':test_user2, 'password': 'not_test'}, follow_redirects=True)
		assert "Password was successfully reset!" in rv.data

		"""Successful login"""
		rv = self.app.post('/login', data={'email': test_user2, 'password': 'not_test'}, follow_redirects=True)
		assert 'Bill' in rv.data
		
		print "second iteration test"
		print "test_change_password passes!"

	def test_change_name(self):
		"""Successful change of name"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test2'

		rv = self.app.post('/edit_setting', data={'firstName': 'Annie', 'lastName': 'Wen', 'email': ""}, follow_redirects=True)
		assert "Successfully made changes" in rv.data
		print "second iteration test"
		print "test_change_name passes!"

	def test_setting_invalid_email(self):
		"""Successful change of name"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test2'

		rv = self.app.post('/edit_setting', data={'firstName': 'Annie', 'lastName': 'Wen', 'email': "asdasd"}, follow_redirects=True)
		assert "Invalid email!" in rv.data
		print "second iteration test"
		print "test_setting_invalid_email passes!"

	def test_change_to_existing_email(self):
		"""Changing to already existing email"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test2'

		rv = self.app.post('/edit_setting', data={'firstName': 'Annie', 'lastName': 'Wen', 'email': 'test@test2'}, follow_redirects=True)
		assert "Email already exists in application!" in rv.data
		print "second iteration test"
		print "test_change_to_existing_email passes!"

	def test_change_email(self):
		"""Changing email"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test2'

		rv = self.app.post('/edit_setting', data={'firstName': 'Annie', 'lastName': 'Wen', 'email': 'test@test1'}, follow_redirects=True)
		assert "Create an account" in rv.data
		print "second iteration test"
		print "test_change_email passes!"

	def test_edit_user_setting(self):
		"""Changing email"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test2'

		rv = self.app.post('/edit_user_setting', data={'firstName': 'Annie', 'lastName': 'Wen', 'email': 'test@test1'}, follow_redirects=True)
		assert "Edit" in rv.data
		print "second iteration test"
		print "test_edit_user_setting passes!"

	def test_settings(self):
		"""Changing email"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test2'

		rv = self.app.post('/settings', data={}, follow_redirects=True)
		assert "Password" in rv.data
		print "second iteration test"
		print "test_settings passes!"

	def test_logout(self):
		"""Changing email"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test2'

		rv = self.app.post('/logout', data={}, follow_redirects=True)
		assert "Forgot Password" in rv.data
		print "second iteration test"
		print "test_logout passes!"

	def test_display_edit(self):
		"""Changing email"""
		with self.app.session_transaction() as sess:
			sess['username']='test@test2'

		rv = self.app.post('/display_edit', data={"ItemName": 'Squash', "Quantity": "1", "Price": "1"}, follow_redirects=True)
		assert "Editing" in rv.data
		print "second iteration test"
		print "test_display_edit passes!"



if __name__ == '__main__':
	unittest.main()
