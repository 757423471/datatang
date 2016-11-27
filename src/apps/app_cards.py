# -*- coding: utf-8 -*-
import os
import re
import sys
import json
from copy import deepcopy
from core.mail import NotifyMailSender
from utils.stocking import fetch_annos
from utils.dateutil import name_as_datetime
from utils.parse import parse_config
from utils.crop import crop, convert
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


def process(db_result, data_dir, img_dir, anno_dir, start, img_format=".png"):
	index = start - 1
	for anno in db_result:
		if anno['effective'] != "1":
			logger.warning("annotation for {0} is noneffective".format(anno['img']))
			continue

		if not anno.get("boxs"):
			logger.warning("no field box in annotation for {0}".format(anno['img']))
			continue

		index += 1
		src_path = os.path.join(data_dir, anno['img'])

		try:
			img_path = os.path.join(img_dir, str(index)+img_format)
			tailor(anno, src_path, img_path)

			anno_path = os.path.join(anno_dir, str(index)+'.txt')
			regulate(anno, anno_path, img_format)

			logger.info("image {0} => {1}".format(anno['img'], str(index)+img_format))
			
		except ValueError as e:
			index -= 1	# revert


def tailor(anno, src_path, dst_path):
	for box in anno['boxs']:
		if box["content"] == "Business_card":
			region = (box['x'], box['y'], box['x']+box['w'], box['y']+box['h'])
			try:
				crop(src_path, dst_path, region)
			except IOError as e:
				logger.error("unresolved path {0}".format(src_path))
				raise ValueError
			return

	# no business card field existed in annotation, just copy the original
	logger.warning("unable to find field `Business_card` for {0}, copied".format(anno['img']))
	convert(src_path, dst_path)


def regulate(anno, dst_path, img_format):
	canonical = ()
	for i, box in enumerate(anno['boxs']):
		if box["content"] == "Business_card":
			canonical = (box['x'], box['y'])
			anno['boxs'].pop(i)
			break

	if not canonical:
		logger.warning("unable to find canonical annotation for {0}".format(anno['img']))
		# raise ValueError
		canonical = (0, 0)
	else:
		for box in anno['boxs']:
			box['x'] -= canonical[0]
			box['y'] -= canonical[1]

	anno['img'] = os.path.basename(dst_path).replace('.txt', img_format)

	del anno['_id']
	del anno['_createTime']
	del anno['_personInProjectId']

	with open(dst_path, 'w') as f:
		f.write(json.dumps(anno, indent=1, ensure_ascii=False).encode('utf-8'))
	

def main():
	config = parse_config()
	title = config.get('project', 'title')
	data = config.get('project', 'data').decode(settings.DEFAULT_DECODING)
	img_path = config.get('product', 'image').decode(settings.DEFAULT_DECODING)
	anno_path = config.get('product', 'anno').decode(settings.DEFAULT_DECODING)
	start = config.getint('product', 'start')
	recipients = config.get('project', 'email')

	product_path = os.path.join(DATA_DIR, 'cards', title.decode(settings.DEFAULT_DECODING))
	img_path = os.path.join(product_path, img_path)
	if not os.path.exists(img_path):
		os.makedirs(img_path)
	anno_path = os.path.join(product_path, anno_path)
	if not os.path.exists(anno_path):
		os.makedirs(anno_path)

	db_result = fetch_annos(title, check=False)
	process(db_result, data, img_path, anno_path, start, ".png")
	if recipients:
		NotifyMailSender(recipients).notify(title)


def usage():
	return "exports tailored bussiness cards and regulative data for coordination"