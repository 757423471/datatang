import os
from datetime import datetime

def name_as_datetime(path, fmt='%b%d-%H%M'):
	name = datetime.now().strftime(fmt) + '.txt'
	return os.path.join(path, name)