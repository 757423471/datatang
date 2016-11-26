# regex module is designed as the pattern - builder
# (see wiki: https://en.wikipedia.org/wiki/Builder_pattern)
# director is in charge of building a regex_processor with correct rules and processors
# products that director gives read same inputs but produce different result
# usage: 
# d = RegexDirecotor()
# r = d.construct(rules).get_regex_proc()
# r.process(text) or r.process_file(filename)
import os
import re
import sys


class BaseRegexException(Exception):
	def __init__(self, msg):
		super(BaseRegexException, self).__init__()
		self.msg = msg
	
	def __repr__(self):
		return self.msg

class IllegalArgumentException(BaseRegexException):
	"""exception for invalid regular expression"""
	

class NotMatchedError(BaseRegexException):
	"""exception for no value"""
	pass

class BuildFailedEerror(BaseRegexException):
	"""incorrect method returned in user-defined builder """
	pass


class RegexDirector(object):
	"""director for building a regex"""
	def __init__(self, builder=None):
		super(RegexDirector, self).__init__()
		self.builder = builder
		self.builder_methods = ["load", "parse", "rules"]
		
	def construct(self, rules):
		self.builder.build_rules(rules)
		self.builder.build_parser()
		self.builder.build_loader()
		self.builder.build_file_processor()
		return self

	def get_regex_proc(self):
		regex_proc = self.builder.regex
		# check all methods were defined well
		for method in self.builder_methods:
			if not getattr(regex_proc, method):
				raise BuildFailedEerror(
					"method {0} is not defined in builder {1}".format(method, self.builder.__class__.__name__))
		return self.builder.regex


class RegexBuilder(object):
	"""substitutes and matches regular expression"""
	RegexObject = re.compile('').__class__

	def __init__(self):
		super(RegexBuilder, self).__init__()
		self.regex = RegexProcessor()

	# place regular expressions or RegexObject at this phase
	# check 
	def build_rules(self, rules):
		raise NotImplementedError

	# uses regular expression from last phase
	def build_parser(self):
		raise NotImplementedError

	# processes text return from last phase
	def build_loader(self):
		raise NotImplementedError

	def build_file_processor(self):
		raise NotImplementedError


class SubBuilder(RegexBuilder):
	"""build a regex processor for substituting"""

	def __init__(self):
		super(SubBuilder, self).__init__()

	# rules for substitute is composed of 2 parts
	# the first part is a regular expression can be compiled
	# and the second is to be replaced
	def build_rules(self, rules):
		legal_rules = []
		for comp, repl in rules:
			if not isinstance(repl, str):
				raise IllegalArgumentException("argument repl {0} is not a string".format(repl))

			if isinstance(comp, str):
				legal_rules.append((re.compile(comp), repl))
			elif isinstance(comp, RegexBuilder.RegexObject):
				legal_rules.append((comp, repl))
			else:
				raise IllegalArgumentException("argument pattern {0} is nether string nor RegexObject".format(comp))
		self.regex.rules = legal_rules

	def build_parser(self):
		# text = reduce(lambda t, r: r[0].sub(r[1], t), rules, text)

		def sub_by_rules(rules, text):
			for comp, repl in rules:
				text = comp.sub(repl, text)
			return text

		self.regex.parse = sub_by_rules

	def build_loader(self):
		self.regex.load = lambda x: x


	def build_file_processor(self):

		def process_file(filename):
			content = []
			with open(filename, 'r') as f:
				for line in f:
					content.append(self.regex.process(line))

			with open(filename, 'w') as f:
				f.write('\n'.join(content))

		self.regex.process_file = process_file


class MatchBuilder(RegexBuilder):
	"""build a regex processor for matching"""
	def __init__(self):
		super(MatchBuilder, self).__init__()
		
	# rules for match is a list of tuple which made up of 2 parts
	# the first part is a regular expression can be compiled
	# and the second lists quotes in the pattern
	def build_rules(self, rules):
		legal_rules = None
		comp, quotes = rules
		if not isinstance(quotes, tuple) and not isinstance(quotes, list):
			raise IllegalArgumentException("{0} is ought to be a sequence of quotes".format(keys))
		if isinstance(comp, str):
			legal_rules = (re.compile(comp), quotes)
		elif isinstance(comp, RegexBuilder.RegexObject):
			legal_rules = (comp, quotes)
		else:
			raise IllegalArgumentException("argument pattern {0} is nether string nor RegexObject".format(comp))

		self.regex.rules = legal_rules

	def build_parser(self):

		def match_by_rules(rules, text):
			comp, quotes = rules
			r = comp.match(text)
			if r:
				return map(lambda q: r.group(r), quotes)
			else:
				raise NotMatchedError("text {0} does not match the pattern".format(text))

		self.regex.parse = match_by_rules

	def build_loader(self):
		self.regex.load = lambda x: x

	def build_file_processor(self):

		def process_file(filename):
			collection = []
			with open(filename, 'r') as f:
				for line in f:
					collection.extend(self.regex.process(line))
			return collection
		self.regex.process_file = process_file


class RegexProcessor(object):
	"""matchs or substitutes according to the the product built"""
	def __init__(self):
		super(RegexProcessor, self).__init__()
		self.rules = None
		self.parse = None
		self.load = None

	def process(self, text):
		return self.load(self.parse(self.rules, text))

	def process_file(self, filename):
		raise NotImplementedError
