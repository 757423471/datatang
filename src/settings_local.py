# -*- coding: utf-8 -*-
# this flie is used to define customized settings
import os

mssql_database = '[10.0.0.201].CrowdDB.dbo'
mssql_tables = {
	'project': '.project',
	'data_result': '.dataresult'
}

apps = [
	'triplelens',
	'dynamo',
]

DEFAULE_DECODING = "gbk" if os.name == "nt" else "utf-8"
DEFAULT_ENCODING = "utf-8"