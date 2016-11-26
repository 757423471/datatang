import copy
from common.finder.literal import TreeMatcher
from common.finder.regexp import RegexDirector, MatchBuilder


def all_are_instances_of(iterable, cls):
	return all(map(lambda o: isinstance(o, cls), iterable))


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

	# removes the ith old child and appends new ones except for i equals -1
	def renew(self, i, repl):
		if i != -1:
			self.children.pop(i)
		if isinstance(repl, list):
			self.children.extend(repl)
		else:
			self.children.append(repl)

	def prune(self):
		children = self.children

		self.children = []
		for child in children:
			if not isinstance(child, TerminalExp):
				child = child.prune()
			self.renew(-1, child)

	@classmethod
	def merge(cls, brothers):
		return brothers


class AlternationExp(NonterminalExp):
	"""node for or"""

	def __init__(self, children):
		super(AlternationExp, self).__init__(children)

	def eval(self, s):
		for child in self.children:
			if child.eval(s):
				return True
		return False


	def prune(self):
		super(AlternationExp, self).prune()

		classes = {}
		for child in self.children:
			classes.setdefault(child.__class__, []).append(child)

		self.children = []
		for cls, objects in classes.items():
			# return it self if only one existed
			self.renew(-1, cls.merge(objects))

		# all the children are the same type
		if len(self.children) == 1:
			child = self.children[0]
			if isinstance(child, AlternationExp) or isinstance(child, TerminalExp):
				return child
		else:
			return self

	@classmethod
	def merge(cls, brothers):
		if len(brothers) == 1:
			return brothers[0]
		else:
			return cls(brothers)


class SequenceExp(NonterminalExp):
	"""node for and"""
	def __init__(self, children):
		super(SequenceExp, self).__init__(children)

	def eval(self, s):
		for child in self.children:
			if not child.eval(s):
				return False
		return True


	def prune(self):
		super(SequenceExp, self).prune()
		if all_are_instances_of(self.children, SequenceExp):
			data = []
			for child in self.children:
				data.extend(child.children)
			self.children = data

		# all the children are the same type
		return self


class NegativeExp(NonterminalExp):
	"""node for not,  only one child was allowed"""

	def __init__(self, children):
		if isinstance(children, AbstractExpression):	# syntax sugar
			children = [children]

		if isinstance(children, list) and len(children) != 1:
			raise ValueError("only one child was allowed for NegativeExp")

		super(NegativeExp, self).__init__(children)

	def eval(self, s):
		return not self.children[0].eval(s)

	def prune(self):
		super(NegativeExp, self).prune()
		return self


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

	def prune(self):
		super(PositiveExp, self).prune()
		return self


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

	@classmethod
	def merge(cls, exps):
		data = reduce(lambda x, y: x+y.data, exps, [])
		return cls(data)


class RegularExp(TerminalExp):
	"""node containing regular expression only"""

	def __init__(self, data):
		if not isinstance(data, list):
			data = [data, ]
		for val in data:
			if not isinstance(val, str) and not isinstance(val, unicode):
				raise ValueError("only string and unicode are accepted as arguments")
		super(RegularExp, self).__init__(data)
		director = RegexDirector(MatchBuilder())
		self.regex_proc = director.construct(data).get_regex_proc()

	def eval(self, s):
		return self.regex_proc.process(s)


class LiteralExp(TerminalExp):
	"""node containing keywords only"""

	def __init__(self, data):
		if not isinstance(data, list):
			data = [data, ]
		for val in data:
			if not isinstance(val, str) and not isinstance(val, unicode):
				raise ValueError("only string and unicode are accepted as arguments")
		
		data = list(set(data))
		super(LiteralExp, self).__init__(data)
		self.tree_matcher = TreeMatcher(data)

	def eval(self, s):
		return self.tree_matcher.search(s)
		

