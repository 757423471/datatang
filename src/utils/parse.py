import os
import inspect
import ConfigParser

import settings

def parse_config():
	caller = os.path.basename(inspect.stack()[1][1])
	if caller.startswith('app_') and caller.endswith('.py'):
		app = caller[4:-3]	# remove app_ and .py
		if app in settings.apps:
			conf = os.path.join(settings.CONF_DIR, app, settings.CONF_IN_USING_NAME)
			if os.path.exists(conf):
				config = ConfigParser.ConfigParser()
				config.read(conf)
				return config
			else:
				print("unable to find config file in {0}".format(conf))
		else:
			print("app name {0} is not registered".format(app))
	else:
		print("caller {0} is not in a standard format".format(caller))