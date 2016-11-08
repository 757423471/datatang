#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import os
import sys
import time
import shutil
import subprocess
import importlib
import hashlib

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

def execute_main(app_name):
	modules = get_apps()

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


def get_apps():
	files = os.listdir(settings.APPS_DIR)
	scripts = filter(lambda x: x.startswith('app_') and x.endswith('.py'), files)	# removes non-python-script
	modules = map(lambda x: x[4:-3], scripts)	# removes 'app_' and '.py'
	return modules


def list_apps():
	modules = get_apps()

	for app_name in modules:
		app = importlib.import_module("apps.app_"+app_name)
		try:
			print("{0} - {1}".format(app_name, app.usage()))
		except AttributeError as e:
			print("\n")


# executing gen_template.py if exists
# else copy app/template.cnf if exists
# else copy conf/common.cnf 
def gen_config(app_name):
	if app_name in settings.apps:
		app_conf_dir = os.path.join(settings.CONF_DIR, app_name)
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

		# if attribute EDITOR was set, display config files in the editor
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

# removes empty and duplicated files in conf/ and data/ 
def clean(app_name):

	def find_empty_or_duplicate(root_path):
		filelist = filter(lambda x: x not in settings.RESERVED_FILES and not x.startswith('.'), os.listdir(root_path))
		filelist = map(lambda x: (os.path.join(root_path, x), os.stat(os.path.join(root_path, x))), filelist)
		# sorts files by last modification time
		sorted_files = sorted(filelist, key=lambda x: x[1].st_mtime, reverse=True)

		hash_vals, to_del = [], []
		for file, status in sorted_files:
			if status.st_size:
				with open(file, 'r') as f:
					hash_val = hashlib.md5(f.read()).hexdigest()
				if hash_val not in hash_vals:
					hash_vals.append(hash_val)
					continue
			to_del.append(file)
		return to_del


	redundant_data = find_empty_or_duplicate(os.path.join(settings.DATA_DIR, app_name))
	redundant_conf = find_empty_or_duplicate(os.path.join(settings.CONF_DIR, app_name))

	def list_then_delete(redundant):
		print "\n".join(map(lambda x: os.path.relpath(x), redundant))
		if raw_input("files listed above will be deleted, are you sure?[y/n]").lower() == 'y':
			for filepath in redundant:
				os.remove(filepath)

	list_then_delete(redundant_data)
	list_then_delete(redundant_conf)


def crontab(app_name, plan=None):
	pass


if __name__ == '__main__':
	app_names = []
	commands = ["run", "gen_config", "list", "clean"]

	callee = {
		"run": (execute_main, "please specify apps to run"),
		"gen_config": (gen_config, "please specify apps to config"),
		"clean": (clean, "please specify apps to be cleaned"),

	}


	me = os.path.basename(sys.argv[0])
	
	if me not in commands:
		print("no such command, please specify a command in {0}".format(commands))
		sys.exit(1)

	if me == "list":
		apps = list_apps()

	# multi arguments needed
	else:
		if len(sys.argv) > 1:
			app_names = sys.argv[1:]
			for app_name in app_names:
				callee[me][0](app_name)
		else:
			print callee[me][1]
			sys.exit(1)



	# TODO: run apps as cron tasks
	if me == "crontab":
		pass


