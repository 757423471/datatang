import re
import os
import sys
import multiprocessing
from settings import logger

class Extractor(multiprocessing.Process):
	"""to extract lines match the given keywords in config files"""

	def __init__(self, theme, keywords, config):
		super(Extractor, self).__init__()
		self.theme = theme
		# a list containing nested 
		self.keywords = keywords
		# TODO: value check
		self.src = config.get('source', '')
		self.dest = config.get('dest', '')
		self.type = config.get('type', 'txt')
		self.target_file = os.path.join(self.dest, self.theme+'.'+self.type)

	def run(self):
		logger.debug("begin to extract for theme - {0}".format(self.theme))
		if not os.path.isfile(self.src):
			logger.error("unable to read source file {0}".format(self.src))
			return
		if not os.path.exists(self.dest):
			logger.debug("unable to find target directories {0}, creating now".format(self.dest))
			os.makedirs(self.dest)




class Interpreter(object):
	"""interprets a given keyword expression, generating a dict indicating their relations (and, or, not)"""
	def __init__(self, relations):
		super(Interpreter, self).__init__()
		self.arg = arg
		
