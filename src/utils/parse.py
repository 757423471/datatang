import os
import inspect
import ConfigParser

import settings
import chardet
import codecs

def parse_config():
	caller = os.path.basename(inspect.stack()[1][1])
	if caller.startswith('app_') and caller.endswith('.py'):
		app = caller[4:-3]	# remove app_ and .py
		if app in settings.apps:
			conf = os.path.join(settings.CONF_DIR, app, settings.CONF_IN_USING_NAME)
			if os.path.exists(conf):
				with open(conf, 'r') as f:
					content = f.read()
					codetype = chardet.detect(content)
					#print codetype
					#print content
					try:
						if codetype['encoding'] == 'utf-8':
							pass
						elif codetype['encoding'] == 'UTF-8-SIG':
							if content[:3] == codecs.BOM_UTF8:
								content = content[3:]
						else:
							content = content.decode('GBK').encode('utf-8')
						
						with open(conf, 'w') as f2:
							f2.write(content)
					except:
						print "Encoding is not supported"

				config = ConfigParser.ConfigParser()
				config.read(conf)
				return config
			else:
				print("unable to find config file in {0}".format(conf))
		else:
			print("app name {0} is not registered".format(app))
	else:
		print("caller {0} is not in a standard format".format(caller))