"""app unit tests"""
# reference: http://www.drdobbs.com/testing/unit-testing-with-python/240165163
import unittest
import pymssql 

from app import app

user_email = "test@test.com"
bill_id = -1

class MyTest(unittest.TestCase):
	"""Test class"""
	def setUp(self):
		"""Set up"""


	def tearDown(self):
		"""Tear down"""

	
	def test_add_item(self):
		"""Add item to bill"""
		global user_email
		global bill_id

		item_name = "test_add_item"
		quantity = 3
		price = 1.50

		cursor = conn.cursor()
		cursor.execute("INSERT INTO Items VALUES (%s, %s, %d, %d, %d)", (user_email, item_name, quantity, price, bill_id))
    	conn.commit()

		cursor = conn.cursor()
		cursor.execute("SELECT * FROM Items WHERE Email=%s AND ItemName=%s AND Quantity=%d AND Price=%d AND BillId=%d", (user_email, item_name, quantity, price, bill_id))
		
		assert cursor.rowcount == 1


	def test_remove_item(self):
		"""Add then remove item from list"""
		global user_email
		global bill_id

		item_name = "test_remove_item"
		quantity = 5
		price = 1.00

		cursor = conn.cursor()
		cursor.execute("INSERT INTO Items VALUES (%s, %s, %d, %d, %d)", (user_email, item_name, quantity, price, bill_id))
    	conn.commit()

		cursor = conn.cursor()
		cursor.execute("SELECT * FROM Items WHERE Email=%s AND ItemName=%s AND Quantity=%d AND Price=%d AND BillId=%d", (user_email, item_name, quantity, price, bill_id))
		
		assert cursor.rowcount == 1

		cursor = conn.cursor()
		cursor.execute("DELETE FROM Items WHERE Email=%s AND ItemName=%s AND Quantity=%d AND Price=%d AND BillId=%d", (user_email, item_name, quantity, price, bill_id))
		conn.commit()

		cursor = conn.cursor()
		cursor.execute("SELECT * FROM Items WHERE Email=%s AND ItemName=%s AND Quantity=%d AND Price=%d AND BillId=%d", (user_email, item_name, quantity, price, bill_id))
		
		assert cursor.rowcount == 0

	def test


if __name__ == '__main__':
	unittest.main()
	db.session.close()
