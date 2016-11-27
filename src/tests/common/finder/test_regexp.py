import re
import unittest
from StringIO import StringIO
from common.finder.regexp import RegexDirector
from common.finder.regexp import SubBuilder, MatchBuilder
from common.finder.regexp import IllegalArgumentException

class RegexTestCase(unittest.TestCase):
    def setUp(self):
        self.regex_director = RegexDirector()
        self.sheet = [
                'Alice was begining to get very tired of sitting by her sister on the bank,',
                'and of having nothing to do: ',
                'once or twice she had peeped into the book her sister was reading',
                'but it had no pictures or conversations in it,',
                '\'and what is the use of a book\' thought Alice',
                '\'without pictures or conversation\'']

    def test_sub_builder(self):
        self.regex_director.builder = SubBuilder()
        with self.assertRaises(IllegalArgumentException):
            self.regex_director.construct([([], 'replace')])
        with self.assertRaises(IllegalArgumentException):
            self.regex_director.construct([('pattern', 1)])
        
        rules = [('\'', '"'), ('(\w+)ing', '\g<1>ed')]
        self.regex_director.construct(rules)
        rp = self.regex_director.get_regex_proc()
        new_sheet = []
        for line in self.sheet:
            new_sheet.append(rp.process(line))

        self.assertEqual(new_sheet[1], 'and of haved nothed to do: ')
        self.assertEqual(new_sheet[5], '"without pictures or conversation"')
