# -*- coding: utf-8 -*-

from core.storage.database import SQLServerHandler, MongoDBHandler
import dynamo_annotation as dynamo


def find_project_id(table, name):
	db_handler = SQLServerHandler()
	result = db_handler.exec_query("select * from {table} where name like '{name}'".format(**locals()))
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

def get_data_result(project_id):
	db_handler = SQLServerHandler()
	result = db_handler.exec_query("select DataGuid, isvalid from [10.0.0.201].CrowdDB.dbo.dataresult where projectid = {project_id}".format(**locals()))
	result = {str(r[0]):r[1] for r in result}
	db_handler.close()
	return result

def get_source_imgs(project_id):
	mongo_handler = MongoDBHandler()
	mongo_handler.set_database(project_id)
	result = []
	for line in mongo_handler.fetch_result():
		result.append(line)
	mongo_handler.close()
	return result


def main():
	project_id = find_project_id('[10.0.0.201].CrowdDB.dbo.project', '%693期图片%')
	if isinstance(project_id, int):
		project_id = str(project_id)
	valid_guid = get_data_result(project_id)
	imgs_result = get_source_imgs(project_id)
	result = dynamo.refine(imgs_result)

	dynamo.process('/Users/imac/Downloads/20160805_g1k17-08-05-2016_15-57-59_idx99', result)