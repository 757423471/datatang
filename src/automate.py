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

def execute_main(app_names):
	modules = os.listdir('apps')
	for mod in modules:
		if mod.endswith('.py') and not mod.startswith('__'):
			mod = mod.split('.')[0]
			app_name = mod.split('_')[-1]
			if app_name in app_names:
				app = importlib.import_module("apps." + mod)
				try:
					print("executing {0}".format(app.__name__))
					app.main()
				except AttributeError as e:
					print("cancelled")

# def temp():
# 	s = SQLDownloader('../data/xianhua.txt', '../data/xianhua')
# 	s.download()

if __name__ == '__main__':
	app_names = []
	if len(sys.argv) > 1:
		app_names = sys.argv
	execute_main(app_names)