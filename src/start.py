#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import os
import sys
import shutil
import subprocess
import importlib

from utils.dateutil import name_as_datetime

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

# executing gen_template.py if exists
# else copy app/template.cnf if exists
# else copy conf/common.cnf 
def gen_template(app_names):
	def copy_new_conf(new_conf, conf_path):
		last_conf = os.path.join(conf_path, settings.CONF_IN_USING_NAME)
		if os.path.exists(last_conf):
			last_conf_bak = filter(lambda x: x.startswith('.').endswith('cfg'), os.listdir(conf_path))
			if len(last_conf_date) == 1:
				shutil.move(last_conf, os.path.join(conf_path, last_conf_bak[1:]))	# back up
				shutil.copy(new_conf, last_conf)	# copy the new config
				shutil.copy(new_conf, name_as_datetime(conf_path, prefix='.', suffix='.cfg'))	# back up date
			else:
				# TODO: find the newest
				sys.exit(1)
		else:
			shutil.copy(new_conf, last_conf)	# copy the new config
			shutil.copy(new_conf, name_as_datetime(conf_path, prefix='.', suffix='.cfg'))	# back up date

	for app in app_names:
		if app in settings.apps:
			app_conf_dir = os.path.join(settings.CONF_DIR, app)
			if not os.path.exists(app_conf_dir):
				os.makedirs(app_conf_dir)
				print("creating directory {0}".format(app_conf_dir))
			script = os.path.join(app_conf_dir, settings.CONF_GEN_SCRIPT_NAME)
			template = os.path.join(app_conf_dir, settings.CONF_TEMPLATE_NAME)
			if os.path.exists(script):
				print("executing custom script to generate config file to {0}".format(app_conf_dir))
				subprocess.check_call(['python', script, app_conf_dir])
			elif os.path.exists(template):
				print("coping template.cfg to {0}".format(app_conf_dir))
				copy_new_conf(template, app_conf_dir)
			else:
				print("coping common.cfg to {0}".format(app_conf_dir))
				copy_new_conf(settings.COMMON_CONF_FILE, app_conf_dir)




if __name__ == '__main__':
	app_names = []
	me = os.path.basename(sys.argv[0])

	if me == "run":
		if len(sys.argv) > 1:
			app_names = sys.argv[1:]
			execute_main(app_names)
		else:
			print('please specify apps to run')
			sys.exit(1)
	
	elif me == "gen_template":
		if len(sys.argv) > 1:
			app_names = sys.argv[1:]
			gen_template(app_names)
		else:
			print('please specify apps to run')
			sys.exit(1)
	else:
		print("no such command, please specify {0}".format("run, gen_template"))

