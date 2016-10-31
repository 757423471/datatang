# -*- coding: utf-8 -*-
import sys

from core.storage.database import SQLServerHandler, MongoDBHandler
from settings import mssql_database, mssql_tables

# look up project id according to its name of batch
def find_project_id(name):
	db_handler = SQLServerHandler()
	result = db_handler.exec_query("select * from {table} where name like '%{name}%'".format(
		table=mssql_database+mssql_tables['project'],
		name=name)
		)
	if result:
		if len(result) > 1:
			print("{0} results found, confirms which one was required: \n")
			for i, line in enumerate(result):
				print("{0}. {1} - {2}".format(i, line[0], line[2].encode('utf-8')))
			project_id = raw_input("enter the project id you need: ")
			#TODO: check the value to see if it was valid
		elif len(result) == 1:
			project_id = result[0][0]
	else:
		print("no result has found")
		project_id = None
	db_handler.close()
	return project_id

# look up sql server to get validity for different guid
def get_validity(project_id):
	db_handler = SQLServerHandler()
	result = db_handler.exec_query("select DataGuid, isvalid from {table} where projectid = {project_id}".format(
		table=mssql_database+mssql_tables['data_result'], 
		project_id=project_id)
		)
	result = {str(r[0]):r[1] for r in result}
	db_handler.close()
	return result

# get result of annotation for project id
def get_anno_result(project_id):
	mongo_handler = MongoDBHandler()
	mongo_handler.set_database(project_id)
	result = []
	for line in mongo_handler.fetch_result():
		result.append(line)
	mongo_handler.close()
	return result

# get all (valid) annotation result in according to the batch name
def fetch_annos(name, check=True):
	project_id = find_project_id(name)
	if not project_id:
		sys.exit(1)

	project_id = str(project_id) if isinstance(project_id, int) else project_id
	anno_result = get_anno_result(project_id)

	if check:
		valid_guid = get_validity(project_id)
		return filter(lambda r: valid_guid.get(r['_guid']), anno_result)
	else:
		return anno_result

