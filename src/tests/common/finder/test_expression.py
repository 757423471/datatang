# -*- coding: utf-8 -*-
import unittest
import copy
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

	def test_merge(self):
		meg = LiteralExp.merge([self.a, self.b])
		self.assertTrue(meg.eval("test a"))
		self.assertTrue(meg.eval("test b"))


class SequenceExpTestCase(unittest.TestCase):
	def setUp(self):
		self.a = LiteralExp('a')
		self.b = LiteralExp('b')
		self.ab = LiteralExp(['a', 'b'])
		self.seq = SequenceExp([self.a, self.b])

	def test_eval(self):
		self.assertTrue(self.seq.eval("a and b"))
		self.assertFalse(self.seq.eval("a and c"))

	def test_prune(self):
		origin = copy.deepcopy(self.seq)
		pruned = self.seq.prune()
		self.assertEqual(pruned, self.seq)

		self.assertEqual(origin.eval('test ab'), pruned.eval('test ab'))
		self.assertEqual(origin.eval('test a'), pruned.eval('test a'))

	def test_prune_all_seq(self):
		c = LiteralExp('c')
		d = LiteralExp('d')
		seq2 = SequenceExp([c, d])
		seq_of_seqs = SequenceExp([self.seq, seq2])

		origin = copy.deepcopy(seq_of_seqs)
		pruned = seq_of_seqs.prune()
		self.assertNotEqual(origin, pruned)
		self.assertEqual(origin.eval('test abcd'), pruned.eval('test abcd'))
		self.assertEqual(origin.eval('test ac'), pruned.eval('test ac'))
		self.assertEqual(origin.eval('test ab'), pruned.eval('test ab'))
		self.assertEqual(origin.eval('test a'), pruned.eval('test a'))


class AlternationExpTestCase(unittest.TestCase):
	def setUp(self):
		self.a = LiteralExp('a')
		self.b = LiteralExp('b')
		self.c = LiteralExp('c')
		self.d = LiteralExp('d')
		self.seq = SequenceExp([self.a, self.b])
		self.ab = LiteralExp(['a', 'b'])
		self.alt = AlternationExp([self.a, self.b])
		self.alt_seq = AlternationExp([self.seq, self.c])

	def test_eval(self):
		self.assertTrue(self.alt.eval("a or c"))
		self.assertFalse(self.alt.eval("d or c"))

		self.assertFalse(self.alt_seq.eval("a test"))
		self.assertTrue(self.alt_seq.eval("a b test"))
		self.assertTrue(self.alt_seq.eval("test c"))
		self.assertFalse(self.alt_seq.eval("test d"))

	def test_prune(self):
		# able to prune
		pruned_alt = self.alt.prune()
		self.assertEqual(pruned_alt.__class__, LiteralExp)
		self.assertEqual(pruned_alt.data, ['a', 'b'])

		# impossible to prune
		pruned_alt_seq = self.alt_seq.prune()
		self.assertEqual(pruned_alt_seq.__class__, AlternationExp)
		self.assertEqual(pruned_alt_seq, self.alt_seq)


	def test_prune_symmetric(self):
		# merge to one
		alt_alts = AlternationExp([self.alt, AlternationExp([self.c, self.d])])
		pruned_alt_alts = alt_alts.prune()
		self.assertEqual(pruned_alt_alts.__class__, LiteralExp)
		self.assertEqual(pruned_alt_alts.data, list(set(['a', 'b', 'c', 'd'])))
	

	def test_prune_unsymmetric(self):
		alt_alt_lit = AlternationExp([self.alt, self.ab])
		pruned_alt_alt_lit = alt_alt_lit.prune()
		self.assertEqual(pruned_alt_alt_lit.data, ['a', 'b'])


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
		