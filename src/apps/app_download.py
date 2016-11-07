import os
import sys
import settings
from base.sql_download import SQLDownloader

RETRIVE_BY_CODE_SQL = """SELECT da.* FROM DataAcquisition da, PersonInProject pip
WHERE pip.ProjectId = {project_id}
AND pip.Code in ({code_set})
AND da.ProjectId = pip.ProjectId
AND da.UserGuid = pip.ProviderUsrGuid
"""

def retrive_urls(project_id, code_set):
	return RETRIVE_BY_CODE_SQL.format(**locals())


def main():
	data_path = os.path.join(settings.DATA_DIR, 'xinanhua')
	conf_file = os.path.join(data_path, 'xianhua.txt')

	s = SQLDownloader(conf_file, data_path)
	s.download()

def usage():
	return "downloads source files according to project id and code"