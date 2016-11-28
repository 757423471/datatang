#!C:\Python27
# -*- coding: utf-8 -*-
import os
import sys
import time
import shutil
import subprocess
import importlib
reload(sys)
sys.setdefaultencoding('utf-8')


#os.chdir('\\src')
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
			print("done")
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
	if not app_name in settings.apps:
		print("app '{0}' is not registered, please make sure it was created before".format(app_name))
	else:
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


def install(app_name):
    if not app_name in settings.apps:
		print("app '{0}' is not registered, please make sure it was created before".format(app_name))
    else:
    	env_dir = os.path.join(settings.ENV_DIR, app_name)
    	if not os.path.exists(env_dir):
    		print("building virtual environment...")
    		env = subprocess.check_call('virtualenv ' + app_name, cwd=settings.ENV_DIR)
    	else:
    		print("virtual environment for {0} was built before".format(app_name))

    	print("activating environment...")
    	vitual_env = os.path.join(env_dir, 'Scripts')
    	old_env = os.environ.copy()
    	import pdb;pdb.set_trace()
    	old_env['PATH'] = vitual_env

    	print("installing packages...")
    	requirement_file = os.path.join(settings.REQS_DIR, app_name+'.req')
    	with open(requirement_file, 'r') as f:
    		for requirement in f:
    			subprocess.check_call('pip install ' + requirement.strip(), shell=True, env=old_env, cwd=vitual_env)
        # subprocess.check_call('pip install' + ' -r ' + requirement_file, env=old_env, cwd=vitual_env)

        print 'done'

def start_app(app_name):
	if app_name in settings.apps:
		print("app {0} was already registered in the settings, choose another name".format(app_name))
		sys.exit(0)
	else:
		targets_to_create = [
			(os.path.join(settings.CONF_DIR, app_name), True),	# path, isdir
			(os.path.join(settings.DATA_DIR, app_name), True),
			(os.path.join(settings.CONF_DIR, app_name, settings.CONF_TEMPLATE_NAME), False),
			(os.path.join(settings.LOGS_DIR, app_name+'.log'), False),
			(os.path.join(settings.REQS_DIR, app_name+'.req'), False),
			(os.path.join(settings.APPS_DIR,'app_'+app_name+'.py'), False),
		]

		for target, isdir in targets_to_create:
			if os.path.exists(target):
				print("path {0} is already existed, if you still want to create a new one, delete it firstly".format(target))
				sys.exit(1)

		for target, isdir in targets_to_create:
			print("creating {0}".format(os.path.relpath(target)))
			if isdir:
				os.makedirs(target)
			else:
				with open(target, 'a') as f:
					pass
		
		app_script = os.path.join(settings.APPS_DIR,'app_'+app_name+'.py')
		with open(app_script, 'w') as f:
			with open(settings.template_app, 'r') as temp:
				f.write(temp.read())
		
		print("done, please register app '{0}' in settings_local.py".format(app_name))


# removes empty and duplicated files in conf/ and data/ 
def clean(app_name):
	to_del = []

	data_path = os.path.join(settings.DATA_DIR, app_name)
	filelist = map(lambda x: os.path.join(data_path, x), os.listdir(data_path))
	filestatus = map(lambda x: (x, os.stat(x)), filelist)

	def empty_files(filestatus):
		empty = []
		for file, status in filestatus:
			if not status.st_size:
				empty.append(file)
		return empty

	# finds all empty files at first
	to_del.extend(empty_files(filestatus))
	filestatus = sorted(filter(lambda x: x not in to_del, filestatus), key=lambda x: x[1].st_ctime)


def crontab(app_name, plan=None):
	pass

#import pdb

#pdb.set_trace()
if __name__ == '__main__':
	app_names = []
	commands = ["run", "gen_config", "list", "clean","install","startapp"]

	callee = {
		"run": (execute_main, "please specify apps to run"),
		"gen_config": (gen_config, "please specify apps to config"),
		"clean": (clean, "please specify apps to clean config and data"),
		"install":(install, "please specify apps to install"),
		"startapp":(start_app, "please specify apps to start")
	}


	me = os.path.basename(sys.argv[1])

	if me not in commands:
		print("no such command, please specify a command in {0}".format(commands))
		sys.exit(1)

	if me == "list":
		apps = list_apps()

	#elif me == "gen_config":
		#if len(sys.argv)>1:
			#app_names = sys.argv[2:]
			#gen_config(app_names)
		

	# multi arguments needed

	else:
		if len(sys.argv) > 1:
			app_names = sys.argv[2:]
			for app_name in app_names:
				callee[me][0](app_name)
		else:
			print callee[me][1]
			sys.exit(1)



	# TODO: run apps as cron tasks
	if me == "crontab":
		pass



