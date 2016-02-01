import os
import sys
import importlib

from base.sql_download import SQLDownloader

try:
	import settings
except ImportError, e:
	sys.stderr.write('Error: Unable to find the file "settings.py" in the directory containing %r' % __file__)
	sys.exit(1)
try:
	import apps
except ImportError, e:
	sys.stderr.write('Error: Unable to find the package "apps" in the directory containing %r' % __file__)
	sys.exit(1)

def execute_newest():
	modules = os.listdir('apps')
	for mod in modules:
		if mod.endswith('.py'):
			mod = mod.split('.')[0]
			app = importlib.import_module(mod)
			app.main()

def temp():
	s = SQLDownloader('../data/xianhua.txt')
	s.download()


if __name__ == '__main__':
	temp()