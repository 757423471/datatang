# load.py - usage: python load.py args
# initial functions to load data, put source list in the initial queue 
# so that pipelining is able to run
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Mar.03
import os
import threading
from core.storage import database, smb_proxy
from core.exceptions import ArgumentsError
from settings import logger

# yield data from specified src,
# src now supports 'smb', 'sqlserver'
class DataSourceFactory(object):
	def __init__(self, src, queue):
		if src == 'smb':
			self.storage = smb_proxy.SMBConnProxy()
		elif src == 'sqlserver':
			self.storage = database.SQLServerHandler()
		else:
			logger.error("unsupported data source: %s " % src)
			raise NotImplementedError('data source not supported')
		self.queue = queue
	
	def retrieve(self, *args, **kwargs):
		self.queue.join()
		try:
			for	data in self.storage.retrieve(*args, **kwargs):
				for t in data:
					self.queue.put(t)
		except ArgumentsError, e:
			logger.error(e.msg)