# -*- coding: utf-8 -*-
import unittest
from common.finder.interpret import LexicalAnalyser
from common.finder.literal import TreeMatcher
from common.finder.expression import SequenceExp, AlternationExp, LiteralExp
from common.finder import factory


class LexicalAnalyserTestCase(unittest.TestCase):
	def setUp(self):
		self.notation_map = {'or': '||', 'and': '&&', 'not': '!', '(': '::(', ')': '::)', }

	def test_init(self):
		itp = LexicalAnalyser(self.notation_map)
		self.assertEqual( itp.tree_matcher.tree.get('|').get('|'), 
			{TreeMatcher._ending: 'or'} )


	def test_parse(self):
		expression = u"::( a || b ::) && ::( c || d::)"
		itp = LexicalAnalyser(self.notation_map)
		syntax_tree = itp.parse(expression)
		self.assertTrue(isinstance(syntax_tree, SequenceExp))
		self.assertTrue(isinstance(syntax_tree.children, list))
		right_child = syntax_tree.children.pop()
		self.assertTrue(isinstance(right_child, AlternationExp))
		right_leaf = right_child.children.pop()
		self.assertTrue(isinstance(right_leaf, LiteralExp))
		self.assertEqual(right_leaf.data, ['a'])

	def test_eval(self):
		expression = u"::( a || b ::) && ::( c || d::)"
		itp = LexicalAnalyser(self.notation_map)
		syntax_tree = itp.parse(expression)

		self.assertTrue(syntax_tree.eval("test a with c"))
		self.assertFalse(syntax_tree.eval("test a"))

	def test_get_operand_interpreter(self):
		expression = u"::( a || b ::) && ::( c || d::)"
		itp = LexicalAnalyser(self.notation_map)

		self.assertEqual(itp.get_operand_interpreter("abc"), factory.LiteralExpInterpreter)
		self.assertEqual(itp.get_operand_interpreter("^test .*"), factory.RegularExpInterpreter)
		self.assertEqual(itp.get_operand_interpreter("mail@\w*?\.com"), factory.RegularExpInterpreter)
		