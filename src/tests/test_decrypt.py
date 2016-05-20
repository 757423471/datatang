import unittest
import random
import mock
from mock import patch

from Crypto.Cipher import AES
from Crypto import Random

from core.handlers.decrypt import AESDecipherer
from tests.testcase import WorkStationTestCase

class AESDeciphererTestCase(WorkStationTestCase):
	
	def setUp(self):
		self.deciphere = super(AESDeciphererTestCase, self).setUp(AESDecipherer)
		
	def test_set_up(self):
		AESDecipherer.decipherer = None
		with patch.dict('settings.DECRYPT_SETTINGS', {'key_path': 'incorrect/path/to/key'}):
			with self.assertRaises(IOError):
				AESDecipherer.set_up()

		self.assertIsNotNone(AESDecipherer.set_up()) 
	
	def test_singleton(self):
		AESDecipherer.decipherer = None
		self.assertEqual(AESDecipherer.set_up(), AESDecipherer.set_up())

	def test_process(self):
		cipher = AESDecipherer.set_up()
		ciphertext1 = cipher.encrypt('the answer is no')
		self.assertEqual(self.deciphere.process((ciphertext1, 'test1')), ('the answer is no', 'test1'))

		rndfile = Random.new()
		text2 = rndfile.read(8192)
		ciphertext2 = cipher.encrypt(text2)			
		self.assertEqual(self.deciphere.process((ciphertext2, 'test2')), (text2, 'test2'))

	def test_decipher(self):
		cipher = AESDecipherer.set_up()
		rndfile = Random.new()

		data = []
		for i in range(10):
			size = random.randint(10, 10000)
			size -= size%16
			data.append((rndfile.read(size), str(i)))

		cipher_data = map(lambda x: (cipher.encrypt(x[0]), x[1]), data)
		self.load_data(cipher_data)
		text_dict = {x[1]:x[0] for x in data}

		while not self.out_queue.empty():
			deciphertext, key = self.out_queue.get(timeout=10)
			self.assertEqual(deciphertext, text_dict[key])

