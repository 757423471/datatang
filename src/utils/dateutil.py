import os
from datetime import datetime

def name_as_datetime(path, fmt='%b%d-%H%M', prefix='', suffix='.txt'):
	name = prefix + datetime.now().strftime(fmt) + suffix
	return os.path.join(path, name)