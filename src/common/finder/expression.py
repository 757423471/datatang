from common.finder.literal import TreeMatcher

class AbstractExpression(object):
	"""abstract class for expression"""
	def __init__(self):
		super(AbstractExpression, self).__init__()
		
	def eval(self, s):
		raise NotImplementedError


class NonterminalExp(AbstractExpression):
	"""base node for all kinds of relationship"""
	def __init__(self, children):
		for child in children:
			if not isinstance(child, AbstractExpression):
				raise ValueError("node's children were only allowd to be instances of AbstractExpression")
		
		super(NonterminalExp, self).__init__()
		self.children = children

	def __str__(self):
		exp = '+ ' + self.__class__.__name__ + '\n' 
		for child in self.children:
			exp += '  ' + str(child)
		return exp


	def eval(self, s):
		raise NotImplementedError


class AlternationExp(NonterminalExp):
	"""node for or"""

	def __init__(self, children):
		super(AlternationExp, self).__init__(children)

	def eval(self, s):
		for child in self.children:
			if child.eval(s):
				return True
		return False

	def replace(self, i, rep):
		self.children[i] = rep

	def prune(self):
		for i, child in enumerate(self.children):
			if not isinstance(child, TerminalExp):
				self.replace(i, child.prune())

		for child in self.children:
			if isinstance(child, self.__class__):
				self.merge(child)


	def merge(self, brother):
		pass


class SequenceExp(NonterminalExp):
	"""node for and"""
	def __init__(self, children):
		super(SequenceExp, self).__init__(children)

	def eval(self, s):
		for child in self.children:
			if not child.eval(s):
				return False
		return True


class NegativeExp(NonterminalExp):
	"""node for not,  only one child was allowed"""

	def __init__(self, children):
		if isinstance(children, AbstractExpression):	# syntax sugar
			children = [children]

		if isinstance(children, list) and len(children) != 1:
			raise ValueError("only one child was allowed for NegativeExp")

		super(NegativeExp, self).__init__(children)

	def prune(self):
		self.children[0].prune()

	def eval(self, s):
		return not self.children[0].eval(s)


class PositiveExp(NonterminalExp):
	"""does nothing, exists when not knowing which to use"""

	def __init__(self, children):
		if isinstance(children, AbstractExpression):	# syntax sugar
			children = [children]
		if isinstance(children, list) and len(children) != 1:
			raise ValueError("only one child was allowed for PositiveExp")
		super(PositiveExp, self).__init__(children)

	def eval(self, s):
		return self.children[0].eval(s)


class TerminalExp(AbstractExpression):
	"""
		base class for expression not representing a boolean logic, 
		meanwhile, implicitely, values in `data` are alternative logic
	"""

	def __init__(self, data):
		super(TerminalExp, self).__init__()
		self.data = data

	def __str__(self):
		return '  - ' + str(self.data) + '\n'

	def eval(self, s):
		raise NotImplementedError


class RegularExp(TerminalExp):
	"""node containing regular expression only"""

	def __init__(self, data):
		if not isinstance(data, list):
			data = [data, ]
		for val in data:
			if not isinstance(val, str) and not isinstance(val, unicode):
				raise ValueError("only string and unicode are accepted as arguments")
		super(RegularExp, self).__init__(data)

	def merge(self, regex):
		pass

	def eval(self, s):
		pass


class LiteralExp(TerminalExp):
	"""node containing keywords only"""

	def __init__(self, data):
		if not isinstance(data, list):
			data = [data, ]
		for val in data:
			if not isinstance(val, str) and not isinstance(val, unicode):
				raise ValueError("only string and unicode are accepted as arguments")
		super(LiteralExp, self).__init__(data)
		self.tree_matcher = TreeMatcher(data)

	def merge(self, litexp):
		pass

	def eval(self, s):
		return self.tree_matcher.search(s)
		

