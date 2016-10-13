import os
import sys
import importlib

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
			app = importlib.import_module("apps." + mod)
			try:
				print("executing {0}".format(app.__name__))
				app.main()
			except AttributeError as e:
				print("cancelled")
				pass

def temp():
	s = SQLDownloader('../data/xianhua.txt', '../data/xianhua')
	s.download()


if __name__ == '__main__':
	execute_newest()