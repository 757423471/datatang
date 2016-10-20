#!/usr/bin/python
# -*- coding: utf-8 -*-
# defined by developers, basically settings are for the system
# rarely needed to be modified

import os
import logging
import logging.config

# dir settings
# PROJECT_ROOT = os.path.dirname(__file__)
PROJECT_ROOT = os.getcwd()
TOOLS_DIR = '%(PROJECT_ROOT)s/../tools' % locals()
DATA_DIR = '%(PROJECT_ROOT)s/../data' % locals()
CONF_DIR = '%(PROJECT_ROOT)s/../conf' % locals()
APPS_DIR = '%(PROJECT_ROOT)s/../apps' % locals()


# config settings
COMMON_CONF_FILE = '%(PROJECT_ROOT)s/conf/common.cfg' % locals() 
CONF_GEN_SCRIPT_NAME = 'gen_template.py'
CONF_TEMPLATE_NAME = 'template.cfg'
CONF_IN_USING_NAME = 'config.cfg'

DAFAULT_TIMEOUT = 60


# database settings

AZURE_SETTINGS = {
	"account": "crowdfile", #容器名
	"key": "LPKAQIkvntlpsZm+EBTB2JfjILpObuRfYzwhmBk31/ILoafSLzwkJaBQDhwcW4rpXks7UGi3+e2+1eCHHCn+SQ==", #容器对应的key值
	"blob_host_base": ".blob.core.chinacloudapi.cn", #blob服务器
	"queue_host_base": ".queue.core.chinacloudapi.cn", #queue服务器
	"queue_name": "auto-cut-queue-%s",
}

MONGODB_SETTINGS = {
	"host": "crowdser.chinacloudapp.cn",
	"port": "37011",
	"user": "crowdadmin",
	"password": "2015_zaixianSimple",
}

SQLSERVER_SETTINGS = {
	"host": "crowdser.chinacloudapp.cn",
	"port": "9280",
	"user": "sa",
	"password": "2015_zaixianSimple",
	"database": "CrowdDB",
	"charset": "UTF-8",
	"reconnect_times": 3,	# limited times to reconnect
	"reconnect_interval": 300,
}

SMB_SETTINGS = {
	"host": "10.10.8.123",
	"port": 139, # 139 if using NetBIOS over tcp/ip, 445 if direct hosting over tcp/ip
	"username": "administrator",
	"password": "Simple1921",
	"domain": "",	# workgroup, it is safe to leave it empty
	"client_name": "DATATANG",	# an arbitary ASCII string	
	"server_name": "WIN-DJM4V2HB0T5",
	# NTLMv1 or NTLMv2 authentication will be used, guess to be True for WIN7, Vista
	"use_ntlm_v2": True,

	"reconnect_times": 3,
	"connect_timeout": 60,
	"echo_timeout": 30,
	"retrive_timeout": 120,
	"reconnect_interval": 300,
}

DECRYPT_SETTINGS = {
	"key_path": os.path.join(TOOLS_DIR, 'key'),
	"timeout": 60,

}

DOWNLOAD_SETTINGS = {
	"queue_buffer": 2500,
	"queue_timeout": 60,
	"download_timeout": 60,
}

# tools are assumed to be put at the dir named tools
TOOLS_SETTINGS = {
	"tuncating_pl": "run_bat.pl",

}

# logs settings
LOGGING_CONF_FILE = '%(PROJECT_ROOT)s/conf/logging.conf' % locals() 
logging.config.fileConfig(LOGGING_CONF_FILE)
logger = logging.getLogger('root')


from settings_local import *

