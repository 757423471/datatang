# -*- coding: utf-8 -*-
import unittest
import Queue

from core.download import Crawler
from tests.testcase import WorkStationTestCase

class CrawlerTestCase(WorkStationTestCase):
	def setUp(self):
		self.crawler = super(CrawlerTestCase, self).setUp(Crawler)

	def test_download(self):
		resource = [('http://www.baidu.com', 'baidu.html'), ('http://www.sina.com', 'sina.html'), ('http://www.163.com', '163.html')]
		self.load_data(resource)

		names = map(lambda x: x[1], resource)
		while not self.out_queue.empty():
			data = self.out_queue.get(timeout=10)
			self.assertNotEqual(data[0], '', 'download failed')
			self.assertNotEqual(names.index(data[1]), -1)

	def test_process(self):
		with self.assertRaises(ValueError):
			self.crawler.process(('www.baidu1.com', 'invalid value'))
		self.assertIsNone(self.crawler.process(('http://www.invalid-url.com', 'invalid url')))