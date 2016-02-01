import os
import base
from core import database, download


class SQLDownloader(base.BaseAutomaton):
	""" """
	def __init__(self, filename):
		super(SQLDownloader, self).__init__()
		self.sql = """SELECT top 10 da.Title, da.FileName, pip.PersonId FROM DataAcquisition da, PersonInProject pip
			WHERE pip.ProjectId = {0} AND pip.Code in ({1})
			AND da.ProjectId = pip.ProjectId AND da.UserGuid = pip.ProviderUserGuid"""
		self.code_cnt = 10
		self.filename = filename
		self.crawler_num = 8
		self.root_dir = '../data/xianhua'

	def set_filename(filename):
		self.filename = filename

	def sql_params(self):
		data = {}
		with open(self.filename) as f:
			for line in f:
				if line.startswith('[') and line.endswith(']\n'):
					project_id = line.replace('[', '').replace(']\n', '')
					data[project_id] = []
				else:
					data[project_id].append(line.replace('\n', ''))
		for key, vals in data.items():
			i = 0
			while i < len(vals):
				yield (key, ', '.join(vals[i:i+self.code_cnt]))
				i += self.code_cnt
				
	def urls_generator(self):
		self.db_handler = database.SQLServerHandler()
		for sql_param in self.sql_params():
			result = self.db_handler.exec_query(self.sql.format(*sql_param))
			yield map(lambda x: (os.path.join(self.root_dir, x[1].split('/')[-1]), x[1]), result)

	def download(self):
		self.downloader = download.Downloader(self.crawler_num)
		self.downloader.dispatch()
		for urls in self.urls_generator():
			self.downloader.queueing(urls)