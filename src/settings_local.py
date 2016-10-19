# -*- coding: utf-8 -*-
# this flie is used to define customized settings
import os

task_list = ["1545", "1546", "1547", "1548", "1549", "1591", "1592", "1593", "1624"]
queue_list = []

for task in task_list:
	queue_list.append("auto-cut-queue-%s"%task)
cutted_queue = "cutted-wav-queue"
cutted_blob = "cutted-wav-blob"
tag_task_list = [('2128', 0), ('2129', 20), ('2130', 40), ('2131', 60), ('2132', 80)]

mssql_database = '[10.0.0.201].CrowdDB.dbo'
mssql_tables = {
	'project': '.project',
	'data_result': '.dataresult'
}

data_location = {
	# 'triplelens': os.path.join(DATA_DIR, 'triplelens'),
	# 'dynamo':  os.path.join(DATA_DIR, 'dynamo'),
}