# -*- coding: utf-8 -*-
import unittest
# import mock
from common.finder.literal import TreeMatcher

class TreeMatcherTestCase(unittest.TestCase):
	def setUp(self):
		self.test_list = ["abc", "abd", "abcde", "bcd"]
		self.test_dict = {1: "abc", 2: "abd", 3: "abcde", 4: "bcd"}

	
	def test_create4list(self):
		tm = TreeMatcher(self.test_list)
		self.assertEqual(tm.tree.get('b').get('c').get('d'), {TreeMatcher._ending: True})
		self.assertEqual(tm.tree.get('b').get('c').get('e'), None)
		self.assertEqual(tm.tree.get('a').get('b').get('c').get(TreeMatcher._ending), True)

	def test_create4dict(self):
		tm = TreeMatcher(self.test_dict)
		self.assertEqual(tm.tree.get('b').get('c').get('d'), {TreeMatcher._ending: 4})
		self.assertEqual(tm.tree.get('b').get('c').get('e'), None)
		self.assertEqual(tm.tree.get('a').get('b').get('c').get(TreeMatcher._ending), 1)

	def test_prunning(self):
		tm = TreeMatcher([])
		self.assertEqual(tm.tree, {})
		tm.prunning(tm.tree, "abc", 1)
		self.assertEqual(tm.tree.get('a').get('b').get('c'), {TreeMatcher._ending: 1})
		tm.prunning(tm.tree, "abd", 2)
		self.assertEqual(tm.tree.get('a').get('b'), {'c': {TreeMatcher._ending: 1}, 'd': {TreeMatcher._ending: 2}})

	def test_search(self):
		tm = TreeMatcher(self.test_dict)
		self.assertEqual(tm.search("test abc"), 1)
		self.assertEqual(tm.search("abcde test with abc"), 3)
		self.assertEqual(tm.search("test"), False)
