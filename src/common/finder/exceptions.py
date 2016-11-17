
class ExpressionError(Exception):
	"""expression was written incorrectly"""
	pass
		
class SyntaxError(ExpressionError):
	"""unable to parse expression"""
	pass		