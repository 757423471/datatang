# -*- coding: utf-8 -*-
import os
import sys
import urllib2
import threading
import Queue
from settings import logger
from settings import download_settings as ds

class Downloader(object):
	"""A controller to download multiple files"""
	def __init__(self, crawler_num, links):
		super(Downloader, self).__init__()
		
	def queueing(self):
		pass

	def dispatch(self):
		pass



class Crawler(threading.Thread):
	"""crawlers to download files in multiple threads"""
	count = 0

	def __init__(self, src_queue, crawler_name):
		super(Crawler, self).__init__()
		self.src_queue = src_queue
		Crawler.count += 1
		self.name = "crawler" + Crawler.count
		logger.info('crawler %s is initialized' % self.name)

	def __del__(self):
		logger.info('crawler %s is destroyed' % self.name)
		Crawler.count -= 1

	def run(self):
		while True:
			(url, filename) = self.src_queue.get()

			try:
				response = urllib2.urlopen(url, timeout=ds['timeout'])
				with open(filename, 'wb') as fp:
					fp.write(response.read())
				self.src_queue.task_done()
			except (HTTPError, URLError) as e:
				logger.error('internet error: %s %s' % (e.code, url))
			except IOError, e:
				logger.error('unable to write to %s' % e.filename)


		
