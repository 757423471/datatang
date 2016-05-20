# -*- coding: utf-8 -*-

import os
import struct

from Crypto.Cipher import AES

from base.workstation import WorkStation
from settings import DECRYPT_SETTINGS as ds
from settings import logger


class Decipherer(WorkStation):
	"""threads to decrypt encrypted files"""
	
	def __init__(self, src_queue, dst_queue):
		super(Decipherer, self).__init__(src_queue, dst_queue)

	@classmethod
	def set_up(cls, *args, **kwargs):
		key_path = kwargs.get('key_path', ds['key_path'])
		try:
			with open(key_path, 'r') as f:
				cls.key = f.read()
				logger.info("the key to be used for decrypting is located at %s" % key_path)
				return cls.key
		except IOError, e:
			logger.error("unable to access the key specified to %s" % key_path)		
			raise e

class AESDecipherer(Decipherer):
	"""Decipherer for AES encrypting"""

	decipherer = None

	def __init__(self, src_queue, dst_queue):
		super(AESDecipherer, self).__init__(src_queue, dst_queue)
		self.timeout = ds.get('timeout')
	
	@classmethod
	def set_up(cls, *args, **kwargs):
		if not cls.decipherer:
			key = super(AESDecipherer, cls).set_up(key_path=ds.get('key_path'))
			# TODO: add exceptions handlers
			cls.decipherer = AES.new(key)
		return cls.decipherer

	@classmethod
	def tear_down(cls):
		cls.decipherer = None

	def process(self, raw_data):
		data, name = raw_data
		try:
			# cipher_text must be a multiple of 16, fill the margin with 0
			data = data if len(data)%16==0 else ''.join([data, '0'*(16-len(data)%16)])
			return (AESDecipherer.decipherer.decrypt(data), name)
		except ValueError, e:
			logger.error(u'unable to decrypt %s by the means of AES' % name)
		