# -*- coding: utf-8 -*-

import os
import re
import json
from utils.stocking import fetch_annos
from utils.parse import parse_config
from utils.dateutil import name_as_datetime
import settings


def load_dictionary(dictionary_path):
	dictionary = {}
	with open(dictionary_path, 'r') as f:
		for line in f:
			items = line.strip().split('\t')
			if len(items) == 2:
				k, v = items
				dictionary[k.strip()] = v.strip().decode('gbk')
			else:
				print(line.decode('gbk'))
	return dictionary

def reverse(dictionary):
	return { v: k for k, v in dictionary.items() }

def process(db_result, dictionary):
	
	def rm_fields(d):
		del d['name']
		del d['bndbox']
		for k, v in d.items():
			if re.match('^indoor_.*?_text$', k):
				del d[k]


	def trans_fields(d):
		key = d["title"].split('-')[-1].strip()
		d["title"] = dictionary[key]

	for anno in db_result:
		del anno['_id']
		del anno['_createTime']

		for bound in anno['object']:
			rm_fields(bound)
			trans_fields(bound)


	return db_result


def main():
	config = parse_config()
	title = config.get('project', 'title')
	db_result = fetch_annos(title, check=False)
	dictionary = load_dictionary(os.path.join(settings.DATA_DIR, 'trans', u'1813室内视频字典.txt'))
	db_result = process(db_result, reverse(dictionary))

	output_filename = name_as_datetime(os.path.join(DATA_DIR,'trans'))

	with open(output_filename, 'w') as f:
		for anno in db_result:
			f.write(json.dumps(anno) + '\n')


def usage():
	return "translates fileds in a json file "