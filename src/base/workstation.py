# -*- coding: utf-8 -*-
import os
import threading
import settings

class WorkStation(threading.Thread):
	"""base class for all stations in the pipelining """
	def __init__(self, src_queue, dst_queue):
		super(WorkStation, self).__init__()
		self.src_queue = src_queue
		self.dst_queue = dst_queue
		self.timeout = settings.DAFAULT_TIMEOUT

	# method to initialize static variables
	@classmethod
	def set_up(cls, *args, **kwargs):
		pass

	@classmethod
	def tear_down(cls, *args, **kwargs):
		pass	

	# different from set_up and tear_down, initialize and destroy is able to operate instance
	# therefore, which should be called after instantiation
	# def initialize(self):
	# 	pass

	# def destroy(self):
	# 	pass

	def mapping(self, cell):
		return cell

	def save(self, data, filename):
		try:
			with open(filename, 'wb') as f:
				f.write(data)
		except IOError, e:
			logger.error('unable to write to %s' % e.filename)

	def run(self):
		while True:
			try:
				raw_data = self.mapping(self.src_queue.get(timeout=self.timeout))
				self.dst_queue.put(self.process(raw_data), timeout=self.timeout)
				self.src_queue.task_done()
			except Exception, e:
				raise e

	# method to be implemented
	# it accepts a tuple, users unpack and process it
	# then return a tuple with packed data
	def process(self, raw_data):
		raise NotImplementedError
