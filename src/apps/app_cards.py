# -*- coding: utf-8 -*-
import os
import re
import sys
import json
from copy import deepcopy

from utils.stocking import fetch_annos
from utils.dateutil import name_as_datetime
from utils.parse import parse_config
from utils.crop import crop
from settings import logger, DATA_DIR
import settings


def import_static(path):
	db_result = []
	with open(path) as f:
		for line_no, line in enumerate(f, start=1):
			try:
				db_result.append(json.loads(line))
			except ValueError as e:
				print("unable to load json string with line num {0}".format(line_no))
	return db_result


def process(db_result, data_dir, img_dir, anno_dir):
	index = 0
	for anno in db_result:
		if anno['effective'] != "1":
			logger.info("annotation for {0} is noneffective".format(anno['img']))
			continue

		index += 1
		src_path = os.path.join(data_dir, anno['img'])
		logger.info("image {0} => {1}".format(anno['img'], str(index)+'.jpg'))

		try:
			img_path = os.path.join(img_dir, str(index)+'.jpg')
			tailor(anno, src_path, img_path)

			anno_path = os.path.join(anno_dir, str(index)+'.txt')
			regulate(anno, anno_path)
			
		except ValueError as e:
			pass


def tailor(anno, src_path, dst_path):
	for box in anno['boxs']:
		if box["content"] == "Business_card":
			region = (box['x'], box['y'], box['x']+box['w'], box['y']+box['h'])
			crop(src_path, dst_path, region)
			return

	logger.error("unable to find annotation for business card in {0}".format(anno['img']))
	raise ValueError

def regulate(anno, dst_path):
	for i, box in enumerate(anno['boxs']):
		if box["content"] == "Business_card":
			canonical = (box['x'], box['y'])
			anno['boxs'].pop(i)
			break

	if not canonical:
		logger.error("unable to find canonical annotation for {0}".format(anno['img']))
		raise ValueError

	for box in anno['boxs']:
		box['x'] -= canonical[0]
		box['y'] -= canonical[1]

	anno['img'] = os.path.basename(dst_path).replace('txt', 'jpg')

	with open(dst_path, 'w') as f:
		f.write(json.dumps(anno, indent=1, ensure_ascii=False).encode('utf-8'))
	

def main():
	config = parse_config()
	title = config.get('project', 'title')
	data = config.get('project', 'data').decode(settings.DEFAULT_DECODING)
	img_path = config.get('product', 'image').decode(settings.DEFAULT_DECODING)
	anno_path = config.get('product', 'anno').decode(settings.DEFAULT_DECODING)

	product_path = os.path.join(DATA_DIR, 'cards', title.decode(settings.DEFAULT_DECODING))
	img_path = os.path.join(product_path, img_path)
	if not os.path.exists(img_path):
		os.makedirs(img_path)
	anno_path = os.path.join(product_path, anno_path)
	if not os.path.exists(anno_path):
		os.makedirs(anno_path)
	
	# db_result = fetch_annos(title, check=False)
	db_result = import_static("/Users/imac/Downloads/769images.txt")
	process(db_result, data, img_path, anno_path)



def usage():
	return "exports tailored bussiness cards and regulative data for coordination"