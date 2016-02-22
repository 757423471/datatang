import os
import sys
from multiprocessing import Process, Pool
from settings import TOOLS_SETTINGS as ts

class Truncator(object):
	"""base class to truncate audio silence"""
	def __init__(self, arg):
		super(Truncator, self).__init__()
		
		