# -*- coding: utf-8 -*-
import os
import sys
import urllib2
import Queue
from cStringIO import StringIO

from base.workstation import WorkStation
from core.storage.smb_proxy import SMBConnProxy
from settings import logger
from settings import DOWNLOAD_SETTINGS as ds

		
class Crawler(WorkStation):
	"""Crawlers to download resource with url"""
	def __init__(self, src_queue, dst_queue):
		super(Crawler, self).__init__(src_queue, dst_queue)

	def process(self, raw_data):
		url, name = raw_data
		try:
			response = urllib2.urlopen(url, timeout=ds.get('download_timeout', 120))
			data = response.read()
			
			return (data, name)
		except urllib2.HTTPError, e:
			logger.error('falied to connect to %s, may for %s' % (url, e.reason))
		except urllib2.URLError, e:
			logger.error('unable to open url %s for %s' % (url, e.reason))


class SMBExtracter(WorkStation):
	"""extract files from smb server"""
	def __init__(self, src_queue, dst_queue):
		self.smb_conn = SMBConnProxy()
		super(SMBExtracter, self).__init__(src_queue, dst_queue)

	def process(self, raw_data):
		service_name, path = raw_data
		file_obj = StringIO()
		try:
			self.smb_conn.retrieve_file(service_name, path, file_obj)
		except OperationFailure, e:
			logger.error('unable to retrieve files in path %s' % path)
			raise e
		data = file_obj.getvalue()
		file_obj.close()
		return (data, os.path.basename(path))