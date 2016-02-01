import os
import sys

class BaseAutomaton(object):
	"""base class to implement an automated processing"""
	def __init__(self):
		super(BaseAutomaton, self).__init__()
	
	# an interface to yield list for urls
	def urls_generator(self):
		raise NotImplementedError

	def retrive_data(self):
		raise NotImplementedError

	def process(self):
		raise NotImplementedError