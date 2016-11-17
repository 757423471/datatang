# -*- coding: utf-8 -*-
import unittest
import Queue
from core.handlers.load import DataSourceFactory

class DataSourceFactoryTestCase(unittest.TestCase):
	def test_smb_retrieve(self):
		queue = Queue.Queue()
		smb_ds = DataSourceFactory('smb', queue)
		
		files_inside = (u'14.肖旸/smbtest/test0/test0_0/5', u'14.肖旸/smbtest/test0/test0_1/6', )
		smb_ds.retrieve(dirs=[u'/E/14.肖旸/smbtest/test0/test0_0', u'/E/14.肖旸/smbtest/test0/test0_1'])
		
		i = 0
		while not queue.empty():
			name, path = queue.get()
			self.assertEqual(name, 'E', 'device found not matched')
			self.assertTrue((path in files_inside), 'redundant path matched: %s' % path)
			i += 1

	def test_sql_retrieve(self):
		pass