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


	def tearDown(self):
		"""Tear down"""

	
	def test_add_item(self):
		"""Add item to bill"""


	def test_remove_item(self):
		"""Add then remove item from list"""

	def test_split_cost(self):
		rv = self.app.post('/split_cost', data=dict(
        Tip='0.2',
        Billid='364',
        Total='2.20'), follow_redirects=True)
    	assert '2.64' in rv.data



if __name__ == '__main__':
	unittest.main()
