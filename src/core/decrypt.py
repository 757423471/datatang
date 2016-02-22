# -*- coding: utf-8 -*-

import os
import struct

from Crypto.Cipher import AES

from workstation import WorkStation
from settings import DECRYPT_SETTINGS as ds
from settings import logger


class Decipherer(WorkStation):
	"""threads to decrypt encrypted files"""
	
	def __init__(self, src_queue, dst_queue):
		super(Decipherer, self).__init__(src_queue, dst_queue)

	@classmethod
	def setup(cls, *args, **kwargs):
		key_path = kwargs.get('key_path', ds['key_path'])
		try:
			with open(key_path, 'r') as f:
				cls.key = f.read()
				return cls.key
				logger.info("the key to be used for decrypting is located at %s" % key_path)
		except IOError, e:
			logger.error("unable to access the key located at %s" % key_path)		


class AESDecipherer(Decipherer):
	"""Decipherer for AES encrypting"""

	decrypter = None

	def __init__(self, src_queue, dst_queue):
		super(AESDecipherer, self).__init__(src_queue, dst_queue)
		self.timeout = ds.get('timeout')
	
	@classmethod
	def setup(cls, *args, **kwargs):
		if not cls.decrypter:
			key = super(AESDecipherer, cls).setup(key_path=ds.get('key_path'))
			# TODO: add exceptions handlers
			cls.decrypter = AES.new(key)
		return cls.decrypter

	def process(self, raw_data):
		data, name = raw_data
		try:
			# else to fill the margin with 0
			data = data[:4096] if len(data)>=4096 else ''.join([data, '0'*(16-len(data)%16)])
			return (AESDecipherer.decrypter.decrypt(data), name)
		except Exception, e:
			logger.error(u'unable to decrypt %s by the means of AES' % name)
		