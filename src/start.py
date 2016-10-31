#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import os
import sys
import time
import shutil
import subprocess
import importlib

os.chdir('./src')
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
	modules = list_apps()

	for app_name in app_names:
		if app_name in modules:
			app = importlib.import_module("apps.app_"+app_name)
			try:
				print("executing {0}".format(app.__name__))
				app.main()
				print("finished")
			except AttributeError as e:
				print("cancelled")
			# subprocess.check_call(['export PYTHONPATH='+settings.PROJECT_ROOT], shell=True)
			# subprocess.check_call(['python', os.path.join(settings.APPS_DIR, mod)])

		else:
			print("app {0} was not found in apps".format(app_name))
			print("enter \"list\" to find all apps")


def list_apps():
	files = os.listdir(settings.APPS_DIR)
	scripts = filter(lambda x: x.endswith('.py') and x.startswith('app_'), files)	# removes non-python-script
	modules = map(lambda x: x[4:-3], scripts)	# removes 'app_' and '.py'
	return modules


# executing gen_template.py if exists
# else copy app/template.cnf if exists
# else copy conf/common.cnf 
def gen_config(app_names):
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
				update_conf(template, app_conf_dir)
			else:
				print("coping common.cfg to {0}".format(app_conf_dir))
				update_conf(settings.COMMON_CONF_FILE, app_conf_dir)

			if settings.EDITOR:
				time.sleep(1)
				conf_file = os.path.join(app_conf_dir, settings.CONF_IN_USING_NAME)
				subprocess.check_call([settings.EDITOR, conf_file])

# replaces the old config file with the new one, meanwhile creating backup files
def update_conf(new_conf, conf_path):
	last_conf = os.path.join(conf_path, settings.CONF_IN_USING_NAME)

	def refresh(new_conf, conf_path, last_conf):
		shutil.copy(new_conf, last_conf)	# copy the new config
		bak_conf = name_as_datetime(conf_path, prefix='.', suffix='.cfg')
		shutil.copy(new_conf, bak_conf)	# back up with name in datename

	if os.path.exists(last_conf):
		last_conf_baks = filter(lambda x: x.startswith('.') and x.endswith('cfg'), os.listdir(conf_path))
		if len(last_conf_baks) == 1:
			last_conf_bak = last_conf_baks[0]
			os.remove(os.path.join(conf_path, last_conf_bak))
			shutil.move(last_conf, os.path.join(conf_path, last_conf_bak[1:]))	# remove dot, then back up
			refresh(new_conf, conf_path, last_conf)
		else:
			print("error: too many invisible files (which starts with .) in {0}, please delete the elders".format(conf_path))
			sys.exit(1)
	else:
		refresh(new_conf, conf_path, last_conf)



if __name__ == '__main__':
	app_names = []
	commands = ["run", "gen_config", "list"]
	me = os.path.basename(sys.argv[0])

	if me == "run":
		if len(sys.argv) > 1:
			app_names = sys.argv[1:]
			execute_main(app_names)
		else:
			print('please specify apps to run')
			sys.exit(1)
	
	elif me == "gen_config":
		if len(sys.argv) > 1:
			app_names = sys.argv[1:]
			gen_config(app_names)
		else:
			print('please specify apps to config')
			sys.exit(1)

	elif me == "list":
		apps = list_apps()
		print('\n'.join(apps))

	# TODO: run apps as cron tasks
	elif me == "crontab":
		pass

	# TODO: removes redundant config files and data
	elif me == "clean":
		pass

	else:
		print("no such command, please specify a command in [{0}]".format(commands))

