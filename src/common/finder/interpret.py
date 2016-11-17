import re
from common.finder.expression import AbstractExpression
from common.finder.factory import *
from common.finder.literal import TreeMatcher


class LexicalAnalyser(object):
	"""scan expression and construct syntax tree"""

	operator_interpreters = {
		'or': AlternationExpInterpreter, 
		'and': SequenceExpInterpreter, 
		'not': NegativeExpInterpreter, 
		'(': OpeningCompositionExpInterpreter, 	# parse in reverse order
		')': ClosedCompositionExpInterpreter,
		'$': TerminalExpInterpreter,
		}

	operand_interpreters = (
		(re.compile('^\w+$', re.UNICODE), LiteralExpInterpreter),
		(re.compile('[|^&.*+?]', re.UNICODE), RegularExpInterpreter),
	)
	
	_final = '$'

	def __init__(self, notation_definition):
		super(LexicalAnalyser, self).__init__()

		notation_handler = {}
		self.tree_matcher = TreeMatcher(notation_definition)

		# for k, v in notation_definition.items():
		# 	notation_handler.setdefault(LexicalAnalyser.operator_interpreter[k], []).append(v)

		# self.notation_tree = TreeMatcher(notation_handler).tree

	def get_operator_interpreter(self, op):
		return self.operator_interpreters.get(op)

	def get_operand_interpreter(self, op):
		for parser, interpreter in self.operand_interpreters:
			if parser.search(op):
				return interpreter

	def parse(self, exp):
		context = {'operands_stack': [], 'operators_stack': [], 'expression': exp, 'op': ''}

		for is_operator, op in self.tree_matcher.findall(exp):
			context['op'] = op
			if is_operator:
				self.get_operator_interpreter(op).create(context)
			else:
				self.get_operand_interpreter(op).create(context)

		return self.get_operator_interpreter(self._final).create(context)	

	# merge children if they all the same nodes
	# lexical_tree was ought to be the value returned by parse, which an instance of AbstractExpression
	def prune(self, lexical_tree):
		if not isinstance(lexical_tree, AbstractExpression):
			raise ValueError("argument lexical_tree was ought to be an instance of AbstractExpression ")
		for child in lexical_tree.children:
			pass



