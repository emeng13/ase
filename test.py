"""Shopping list unit tests"""
# reference: http://www.drdobbs.com/testing/unit-testing-with-python/240165163
import unittest

from shopping_list import app, db
from shopping_list import shopping_list

class MyTest(unittest.TestCase):
	"""Test class"""
	def setUp(self):
		"""Set up"""
		app.config['TESTING'] = True
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
		self.app = app.test_client()
		db.create_all()

	def tearDown(self):
		"""Tear down"""
		db.session.remove()
		db.drop_all()

	def test_add_item(self):
		"""Add item to list"""
		l1 = shopping_list(name='test1', quantity='1')
		db.session.add(l1)
		db.session.commit()

		assert l1 in db.session

	def test_remove_item(self):
		"""Add then remove item from list"""
		l2 = shopping_list(name='test2', quantity='2')
		db.session.add(l2)
		db.session.commit()

		assert l2 in db.session

		db.session.delete(l2)
		db.session.commit()

		testname = 'test2'

		q = shopping_list.query.filter_by(name=testname).first()

		assert q is None


if __name__ == '__main__':
	unittest.main()
	db.session.close()
