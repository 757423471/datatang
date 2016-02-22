import unittest

from core.decrypt import AESDecipherer

class AESDeciphererTestCase(unittest.TestCase):
	
	def setUp(self):
		self.deciphere = super(AESDeciphererTestCase, self).setUp(AESDecipherer)
		