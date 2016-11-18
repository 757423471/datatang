# -*- coding: utf-8 -*-

import os
import re

from utils.parse import parse_config
from utils.dateutil import name_as_datetime
from utils.serialize import load_csv, dump_csv
from settings import logger
import settings

# amends the first column if there was no data
def patch(table, header=3):
	prev = ''
	for row in table[header:]:
		if row[0]:
			prev = row[0]
		else:
			row[0] = prev
	return table

def exports(clusters, header, themes, path):
	for theme in themes:
		content = clusters.get(theme)
		if content:
			for row in header[::-1]:
				content.insert(0, row)
			dump_csv(content, os.path.join(path, theme+'.csv'))
		else:
			logger.info("no content for theme {0}".format(theme))


def concatenate(source, categories):
	tables = { c: [] for c in categories }
	filenames = os.listdir(source)
	for category in categories:
		for filename in filenames:
			if filename.find(category) != -1:
				table = load_csv(os.path.join(source, filename))
				if tables[category]:
					table = table[3:]
				tables[category].extend(table)
	return tables


def get_header(table):
	return table[:3]


def classify(table, header=3):
	clusters = {}
	for row in table[header:]:
		clusters.setdefault(row[1], []).append(row)

	encoded_cluster = {}
	for k, v in clusters.items():
		encoded_cluster[k.decode('gbk').encode('utf-8')] = v

	logger.info("{0} categories are classified, they are {1}".format(len(clusters), ', '.join(map(lambda x: x.decode('gbk').encode('utf-8'), clusters.keys()))))
	return encoded_cluster

def theme_in_category(themes, category):
	return map(lambda x: x[-1], filter(lambda y: y[0].find(category) != -1, map(lambda z: z.split('-'), themes)))


def main():
	config = parse_config()
	source = config.get('data', 'source')
	categories = config.get('data', 'categories').split(',')
	themes = config.get('data', 'themes').split(',')

	tables = concatenate(source, categories)

	product_dir = name_as_datetime(os.path.join(settings.DATA_DIR, 'xlsxsplit'), suffix='')
	if not os.path.isdir(product_dir):
		os.makedirs(product_dir)

	for category in categories:
		table = tables.get(category)
		header = get_header(table)
		clusters = classify(patch(table))
		theme = theme_in_category(themes, category)
		exports(clusters, header, theme, product_dir)


def usage():
	return "split an excel form into several sheets according to a field"
