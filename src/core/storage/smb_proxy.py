# -*- coding: utf-8 -*-
# smb_proxy.py - usage: SMBConnProxy().create()
# delegant to provide reusable connections to access smb server
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Mar.03
import os
import re
from cStringIO import StringIO

from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure

from base.workstation import WorkStation
from core.exceptions import ArgumentsError
from settings import SMB_SETTINGS as ss
from settings import logger

MAX_INTERVAL = 500

# differs from database, 
# smb connection may be reset by the remote server for idling
class SMBConnProxy(object):
	"""inherited class to establish a new connection if the old was reset"""
	def __init__(self, *args, **kwargs):
		self.username = ss['username']
		self.password = ss['password']
		self.client_name = ss['client_name']
		self.server_name = ss['server_name']
		self.use_ntlm_v2 = ss['use_ntlm_v2']

		self.ip = ss['host']
		self.port = ss['port']
		self.smb_conn = self.__connect()
		self.__override()

	def __del__(self):
		try:
			self.smb_conn.close()
		except AttributeError, e:
			pass

	def __override(self):
		for key in SMBConnection.__dict__.keys():
			try:
				self.__getattribute__(key)
			except AttributeError, e:
				self.__setattr__(key, getattr(self.smb_conn, key, None))

	def __connect(self):
		conn_cnt = 0
		logger.info('trying to connect smb server on %s:%s' % (self.ip, self.port))
		while conn_cnt < ss.get('reconnect_times', 3):
			try:
				smb_conn = SMBConnection(self.username, self.password, self.client_name, self.server_name, use_ntlm_v2=self.use_ntlm_v2)
				smb_conn.connect(self.ip, self.port)
				logger.info('connected to smb server')
				return smb_conn
			except Exception, e:
				conn_cnt += 1
				logger.info('connecting failed, times to reconnect: %d' % conn_cnt)
		return None

	def connect(self):
		while not self.is_connected:
			self.smb_conn = self.__connect()
			if not self.smb_conn:
				interval = random.randint(0, ss.get('reconnect_interval', MAX_INTERVAL))
				logger.info('connection will be established in %ss' % interval)
				time.sleep(interval)
		return self.smb_conn
	
	@property
	def is_connected(self):
		return self.smb_conn.sock


	def retrieve_file(self, shared_device, root_dir, file_obj, timeout=60):
		if not self.is_connected:
			logger.warning('connection was reset, reconnecting...')
			self.smb_conn = self.connect()

		self.smb_conn.retrieveFile(shared_device, root_dir, file_obj, timeout)


	# traverse the root_dir to get filelist
	def get_filelist(self, shared_device, root_dir, search=55, pattern='*'):
		shared_dirs = [root_dir]
		# extracted until no files existed
		shared_files = []
		if not self.is_connected:
			self.smb_conn = self.connect()

		while shared_dirs:
			path= shared_dirs.pop()
			# classifies files in the list, 
			try:
				shared_items = self.smb_conn.listPath(shared_device, path, search, pattern)
			except OperationFailure, e:
				logger.error('unable to access the path %s' % root_dir)
			else:
				for item in shared_items:
					file_path = os.path.join(path, item.filename)
					if item.filename.startswith('.'):
						logger.warning('path %s starts with ".", ignored' % file_path)
						continue
					if item.isDirectory:
						shared_dirs.append(file_path)
					else:
						shared_files.append((shared_device, file_path))

		logger.info('%d files are retrieved in the directory %s' % (len(shared_files), root_dir))
		return shared_files

	def retrieve(self, *args, **kwargs):
		dirs = kwargs.get('dirs', [])
		pattern = kwargs.get('pattern', '*')
		for dir_path in dirs:
			r = re.match('^/(?P<service_name>.+?)/(?P<path>.+)$', dir_path, re.UNICODE)
			if r:
				yield self.get_filelist(r.group('service_name'), r.group('path'), pattern=pattern)
			else:
				logger.error('unable to parse the path: %s' % dir_path)
				continue
			
