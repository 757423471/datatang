# -*- coding: utf-8 -*-
# database.py - provides uniform interfaces to query or modify the database
# authors: Liu Size, Xiao Yang<xiaoyang0117@gmail.com>
# date: 2016.01.28

import sys
import time
import random
import pymssql
from pymongo import MongoClient, errors
from core.exceptions import ArgumentsError, ConnectionError
from settings import SQLSERVER_SETTINGS as ss
from settings import MONGODB_SETTINGS as ms
from settings import logger

MAX_INTERVAL = 500

class SQLServerHandler(object):
	"""an instance to query and modify data in the sqlserver"""
	def __init__(self):
		super(SQLServerHandler, self).__init__()
		self.conn = self.__connect()

	def __del__(self):
		try:
			self.conn.close()
		except AttributeError,e:
			pass

	# not guaranteed, try to connect in 3 times
	def __connect(self):
		conn_cnt = 0
		logger.info('trying to connect to sqlserver on %s:%s' % (ss.get('host'), ss.get('port')))
		while conn_cnt < ss.get('reconnect_times', 3):
			try:
				conn = pymssql.connect(host=ss.get('host'), port=ss.get('port'), user=ss.get('user'),\
					password=ss.get('password'), database=ss.get('database'), charset=ss.get('charset'))
				logger.info("connected to sqlserver")
				return conn
			except Exception, e:	# TODO:add a specified exception
				conn_cnt += 1
				logger.info('connecting failed, times to reconnect: %d' % conn_cnt)
		
		logger.warning('unable to establish a connection, waiting for the next time')
		return None

	def close(self):
		try:
			self.conn.close()
			self.conn = None
			self.cursor = None
		except AttributeError, e:
			logger.error('connection closed already, invalid call')
			raise AttributeError
	
	# guarantee to return a reliable connection
	def connect(self):
		while not self.conn:
			self.conn = self.__connect()
			if not self.conn:
				interval = random.randint(0, ss.get('reconnect_interval', MAX_INTERVAL))
				logger.info('connection will be established in %ss' % interval)
				time.sleep(interval)
		return self.conn

	def exec_query(self, sql_query):
		if not sql_query:
			logger.warn('invalid sql with no content')
			return
		if not self.conn:
			self.conn = self.connect()
		
		self.cursor = self.conn.cursor()
		
		try:
			logger.info('executes sql: "%s"' % sql_query)
			self.cursor.execute(sql_query)
			result = self.cursor.fetchall()
		except Exception as e:
			logger.error(e)
			return

		if result:
			logger.info('quering executed successfully')
		else:
			logger.info('quering executed with no result')
		return result

	# to add, delete and update
	def exec_commit(self, sql_commit):
		if not sql_commit:
			logger.error("invalid sql with no content")
			return
		if not self.conn:
			self.conn = self.connect()
		self.cursor = self.conn.cursor()

		try:
			logger.info('executes sql: %s' % sql_commit)
			self.cursor.execute(sql_commit)
			self.conn.commit()
		except Exception as e:
			logger.error(e)
			return 
		
		logger.info('sql executed successfully')

	#TODO: execute many at one time
	#self.cursor.executemany() 
	def exec_many(self, sql, arg):
		raise NotImplementedError

	def retrieve(self, *args, **kwargs):
		pass


class MongoDBHandler(object):
	def __init__(self):
		super(MongoDBHandler, self).__init__()
		self.client = self.__connect()

	def __del__(self):
		try:
			self.client.close()
		except AttributeError,e:
			pass

	def __connect(self):
		mongo_url = self.__get_mongo_url(ms['user'], ms['password'], ms['host'], ms['port'])
		logger.info("connectting to {0}".format(mongo_url))
		client = MongoClient(mongo_url)
		try:
			client.address
		except errors.ServerSelectionTimeoutError as e:
			logger.error("timed out to connect {0}".format(mongo_url))
			raise exceptions.ConnectionError("connecting timeout")
		else:
			logger.info("connected")
			return client

	def __get_mongo_url(self, user, password, host, port):
		if user and password and host and port:
			return "mongodb://{user}:{password}@{host}:{port}".format(**locals())
		else:
			logger.error("infomation is not complete, unable to return a valid mongo url")
			raise ArgumentsError(user=user, password=password, host=host, port=port)

	def set_database(self, db_name):
		self.db_name = db_name
		self.db = self.client[db_name]
		

	def fetch(self, table, cond):
		try:
			for item in getattr(self.db, table).find(cond):
				yield item
		except errors.ServerSelectionTimeoutError as e:
			logger.error("timed out to fetch {0}".format(table))
			raise exceptions.ConnectionError("connecting timeout")

	def fetch_source(self, cond={}):
		try:
			for item in self.db.Source.find(cond):
				yield item
		except errors.ServerSelectionTimeoutError as e:
			logger.error("timed out to fetch {0}".format(table))
			raise exceptions.ConnectionError("connecting timeout")

	def fetch_result(self, cond={}):
		try:
			for item in self.db.Result.find(cond):
				yield item
		except errors.ServerSelectionTimeoutError as e:
			logger.error("timed out to fetch {0}".format(table))
			raise exceptions.ConnectionError("connecting timeout")

	def close(self):
		self.client.close()
			


