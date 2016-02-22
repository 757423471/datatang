# -*- coding: utf-8 -*-
import os
import sys
import urllib2
import threading
import Queue

from core.workstation import WorkStation
from settings import logger
from settings import DOWNLOAD_SETTINGS as ds

		
class Crawler(WorkStation):
	"""Crawlers to download resource"""
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
