
from settings import logger


class AstaryException(Exception):
	""" unable to find the leaf finally"""
	pass


class TreeMatcher(object):
	"""a matcher implemented in the idea of tree"""
	_ending = None

	def __init__(self, branches):
		super(TreeMatcher, self).__init__()
		self.tree = {}
		self.branches = branches
		self.__create()

	# TODO: a more pretty tree
	def __str__(self):
		return repr(self.tree)

	# TODO: yields in order
	def __iter__(self):
		raise NotImplementedError

	def __create(self):
		if isinstance(self.branches, list):
			self.create4list(self.branches)
		elif isinstance(self.branches, dict):
			self.create4dict(self.branches)
		else:
			raise NotImplementedError


	# branches = [word1, word2, word3 ... ]
	def create4list(self, branches, leaf=True):
		for branch in branches:
			self.prunning(self.tree, branch, leaf)

	# branches = {leaf1: [word1, word2, ...], leaf2 : ... }
	def create4dict(self, leaves):
		for leaf, branches in leaves.items():
			if not isinstance(branches, list):
				branches = [branches]
			for branch in branches:
				self.prunning(self.tree, branch, leaf)
	

	# adds a branch for the tree
	def prunning(self, root, branch, leaf):
		node = root 	# starts from root
		end = len(branch)-1
		for i, joint in enumerate(branch):
			# given a leaf if it arrives at the end else a new brach
			node = node.setdefault(joint, {} if i<end else {TreeMatcher._ending: leaf})

	def search(self, line):

		# differs from search, the first value in the phrase was definitely matched
		def match(tree, phrase):
			branch = tree
			try:
				for i, milestone in enumerate(phrase, start=1):
					branch = branch[milestone]
			except KeyError, e:
				pass

			if not branch.get(TreeMatcher._ending):
				raise AstaryException('Unable to get the leaf.')
			else:
				return branch[TreeMatcher._ending]	# arrives at the end
		
		i = 0
		while i < len(line):
			if self.tree.get(line[i]):
				try:
					key = match(self.tree, line[i:])
					return key
				except AstaryException as e:
					pass # a failed trial
			i += 1

		return False

	# TODO: find all matched keys
	def findall(self, exp):
		other = ''
		start = 0

		while start < len(exp):
			letter = exp[start]
			if self.tree.get(letter):
				subtree = self.tree[letter]
				i = start + 1

				while i <= len(exp):
					if i < len(exp) and subtree.get(exp[i]):	# ends with notations when i equals to len(exp)
						subtree = subtree[exp[i]]
						i += 1						
					else:
						if subtree.get(TreeMatcher._ending):	# found
							if other.strip():	# 
								yield False, other.strip()
							
							yield True, subtree.get(TreeMatcher._ending)
							
							other = letter = ''
							start = i - 1
						break

			other += letter
			start += 1

		if other.strip():
			yield False, other


	# TODO: combines with another a tree
	def merge(self, tree_matcher):
		pass


	# TODO:extracts all matched lines in a file
	def extract(self, file_name):
		pass