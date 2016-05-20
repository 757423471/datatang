# -*- coding: utf-8 -*-

class ArgumentsError(Exception):
	def __init__(self, *args, **kwargs):
		args_passed = str(args) + str(kwargs)
		self.msg = 'arguments passed not as requirement: ' + args_passed
		super(ArgumentsError, self).__init__()