import os
import sys

RETRIVE_BY_CODE_SQL = """SELECT da.* FROM DataAcquisition da, PersonInProject pip
WHERE pip.ProjectId = {project_id}
AND pip.Code in ({code_set})
AND da.ProjectId = pip.ProjectId
AND da.UserGuid = pip.ProviderUsrGuid
"""

def retrive_urls():
	RETRIVE_BY_CODE_SQL.format()