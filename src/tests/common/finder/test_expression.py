# -*- coding: utf-8 -*-
import unittest
from common.finder.interpret import LexicalAnalyser
from common.finder.literal import TreeMatcher
from common.finder.expression import SequenceExp, AlternationExp, NegativeExp, LiteralExp


class LiteralExpTestCase(unittest.TestCase):
	def setUp(self):
		self.a = LiteralExp('a')
		self.b = LiteralExp('b')
		self.ab = LiteralExp(['a', 'b'])

	def test_eval(self):
		self.assertTrue(self.a.eval('test a'))
		self.assertTrue(self.ab.eval('test b'))
		self.assertFalse(self.ab.eval('test c'))
		

class SequenceExpTestCase(unittest.TestCase):
	def setUp(self):
		a = LiteralExp('a')
		b = LiteralExp('b')
		self.ab = LiteralExp(['a', 'b'])
		self.seq = SequenceExp([a, b])

	def test_eval(self):
		self.assertTrue(self.seq.eval("a and b"))
		self.assertFalse(self.seq.eval("a and c"))


class AlternationExpTestCase(unittest.TestCase):
	def setUp(self):
		a = LiteralExp('a')
		b = LiteralExp('b')
		c = LiteralExp('c')
		ab = LiteralExp(['a', 'b'])
		seq = SequenceExp([a, b])
		self.alt = AlternationExp([a, b])
		self.alt_seq = AlternationExp([seq, c])

	def test_eval(self):
		self.assertTrue(self.alt.eval("a or c"))
		self.assertFalse(self.alt.eval("d or c"))

		self.assertFalse(self.alt_seq.eval("a test"))
		self.assertTrue(self.alt_seq.eval("a b test"))
		self.assertTrue(self.alt_seq.eval("test c"))
		self.assertFalse(self.alt_seq.eval("test d"))

class NegativeExpTestCase(unittest.TestCase):
	def setUp(self):
		a = LiteralExp('a')
		b = LiteralExp('b')
		alt = AlternationExp([a, b])
		seq = SequenceExp([a, b])
		self.neg_seq = NegativeExp(seq)

	def test_eval(self):
		self.assertFalse(self.neg_seq.eval("a and b"))
		self.assertTrue(self.neg_seq.eval("a and c"))
		