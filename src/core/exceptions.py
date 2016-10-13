# -*- coding: utf-8 -*-
class BaseException(Exception):
	def __init__(self, msg):
		super(BaseException, self).__init__()
		self.msg = msg
		

class ArgumentsError(BaseException):
	def __init__(self, msg='arguments passed not as requirement: ', **kwargs):
		super(ArgumentsError, self).__init__(msg)
		self.kwargs = kwargs

	def __repr__(self):
		resp = "arguments passed as belows: \n"
		for k, v in self.kwargs.items():
			resp += "{0}: {1};".format(k, v)
		return resp

class ConnectionError(BaseException):
	pass