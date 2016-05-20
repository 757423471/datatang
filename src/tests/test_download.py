# -*- coding: utf-8 -*-
import unittest
from core.handlers.download import Crawler, SMBExtracter
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

	def test_process_failed(self):
		with self.assertRaises(ValueError):
			self.crawler.process(('www.baidu1.com', 'invalid value'))
		# may failed for redirecting
		self.assertIsNone(self.crawler.process(('http://www.invalid-url.com', 'invalid url')))


class SMBExtracterTestCase(WorkStationTestCase):
	def setUp(self):
		self.smb_extracter = super(SMBExtracterTestCase, self).setUp(SMBExtracter)

	def test_process(self):
		data = [('E', u'/14.肖旸/smbtest/test0/1'), ('E', u'/14.肖旸/smbtest/test0/2'), ('E', u'/14.肖旸/smbtest/test0/3'), ('E', u'/14.肖旸/smbtest/test0/4')]
		super(SMBExtracterTestCase, self).load_data(data)
		
		counter = 0
		while not self.out_queue.empty():
			counter += 1
			val, name = self.out_queue.get(timeout=60)
			self.assertEqual(val, name, 'did not extract correct files')
		self.assertEqual(counter, len(data), 'data lost in processing')

