from common.finder import expression as exp
from common.finder import exceptions

class AbstractExpInterpreter(object):
	"""abstract class for expression factory"""
	def __init__(self):
		super(AbstractExpInterpreter, self).__init__()

	@classmethod
	def create(cls, op, context):
		raise NotImplementedError

	@classmethod
	def product(cls):
		raise NotImplementedError

class OperatorInterpreter(AbstractExpInterpreter):
	"""base class for creating non-terminal expression instance"""

	def __init__(self):
		super(OperatorInterpreter, self).__init__()
	
	@classmethod
	def create(cls, context):
		context['operators_stack'].append(cls.hook)

	@classmethod
	def pop_operand(cls, context):
		return context['operands_stack'].pop()

	@classmethod
	def push_operand(cls, context, operand):
		context['operands_stack'].append(operand)

	@classmethod
	def pop_operator(cls, context):
		return context['operators_stack'].pop()

	@classmethod
	def is_terminated(cls, context):
		return len(context['operators_stack']) == 0 and len(context['operands_stack']) == 1 

	@classmethod
	def hook(cls, context):
		cls.born(context, cls._argc)

	# pop `argc` operand(s) to generate a new operand
	@classmethod
	def born(cls, context, argc):
		args = []
		for i in range(argc):
			args.append(cls.pop_operand(context))
		cls.push_operand(context, cls._product_cls(args))



class AlternationExpInterpreter(OperatorInterpreter):
	"""facotry class for AlternationExp"""
	_product_cls = exp.AlternationExp
	_argc = 2


class SequenceExpInterpreter(OperatorInterpreter):
	"""factory class for SequenceExp"""
	_product_cls = exp.SequenceExp
	_argc = 2
		

class NegativeExpInterpreter(OperatorInterpreter):
	"""factory class for NegativeExpInterpreter"""
	_product_cls = exp.NegativeExp
	_argc = 1
		

class OpeningCompositionExpInterpreter(OperatorInterpreter):
	"""usually for left bracket"""
	
	# stop iteration 
	@classmethod
	def hook(cls, context):
		raise StopIteration


class ClosedCompositionExpInterpreter(OperatorInterpreter):
	"""as opposed to OpeningCompositionExpInterpreter, usually for right bracket"""
	
	# stop moving forward, call hooks until OpeningCompositionExpInterpreter
	@classmethod
	def create(cls, context):
		try:
			while True:
				operator = cls.pop_operator(context)
				operator(context)
		except StopIteration as e:
			return

	@classmethod
	def hook(cls, context):
		raise NotImplementedError


class TerminalExpInterpreter(OperatorInterpreter):
	"""which represents time to eval all operator expression"""

	@classmethod
	def create(cls, context):
		try:
			while True:
				operator = cls.pop_operator(context)
				operator(context)
		except StopIteration as e:
			raise exceptions.SyntaxError
		except IndexError as e:
			if cls.is_terminated:
				return cls.pop_operand(context)

	@classmethod
	def hook(cls, context):
		raise NotImplementedError
	
class OperandInterpreter(AbstractExpInterpreter):
	"""base class for creating terminal expression"""

	@classmethod
	def create(cls, context):
		operand = cls._product_cls(context['op'])
		context['operands_stack'].append(operand)


class LiteralExpInterpreter(OperandInterpreter):
	"""interpreter to create literal expression"""
	_product_cls = exp.LiteralExp


class RegularExpInterpreter(OperandInterpreter):
	"""to create regular expression node"""
	_product_cls = exp.RegularExp
	

		