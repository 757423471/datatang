# wrapper.py - usage: python wrapper.py args
# idea depicted in python cookbook 9.1, which wraps all callable functions with before/after
# author: xiao yang <xiaoyang0117@gmail.com>
# date: 2016.Mar.04


import inspect

class GenericWrapper(object):
	"""wrap all methods with before and after"""
	def __init__(self, obj, before, after, ignore=()):
		pass
