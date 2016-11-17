import unittest
import Queue

from base.workstation import WorkStation

class WorkStationTestCase(unittest.TestCase):
	def setUp(self, cls):
		self.in_queue = Queue.Queue()
		self.out_queue = Queue.Queue()
		self.instance = cls(self.in_queue, self.out_queue)
		self.instance.setDaemon(True)
		self.instance.start()
		return self.instance

	def load_data(self, data):
		for t in data:
			self.in_queue.put(t)
		self.in_queue.join()
