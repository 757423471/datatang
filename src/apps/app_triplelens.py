# -*- coding: utf-8 -*-
import os
import re
import sys
from copy import deepcopy

from utils.stocking import fetch_annos
from utils.dateutil import name_as_datetime
from utils.parse import parse_config
from settings import logger, DATA_DIR


lens_orientation = {
	'center': 0,
	'left': 1,
	'right': 2,
}

def refine(db_result):
	images = []
	for record in db_result:
		record = record['rdata']

		center = extract_annos(record['images'], lens_orientation['center'])
		left = extract_annos(record['imagesL'], lens_orientation['left'])
		right = extract_annos(record['imagesR'], lens_orientation['right'])

		# if topk:
		# 	annoted_frames = sorted(center.keys())[:topk]
		# 	center = subset(center, annoted_frames)
		# 	left = subset(left, annoted_frames)
		# 	right = subset(right, annoted_frames)

		detect_overlapped(center, [left, right])
		detect_overlapped(left, [center, right])
		
		images.append([center, left, right])

	# import pdb;pdb.set_trace()
	return images


def subset(full_set, sub_set):
	d = {}
	for key in sub_set:
		d[key] = full_set[key]
	return d


def detect_overlapped(primary, minors):
	for frame, annos in primary.items():
		for track_name, track_info in annos.items():
			for minor in minors:
				if minor[frame].get(track_name):
					track_info['overlapped'] = 1
					minor[frame][track_name]['overlapped'] = 1



def extract_annos(images, image_id):
	annos = {}
	frame_parser = re.compile('.+image(\d+).jpg')

	for image in images:
		try:
			# print image['fileName']
			frame_id = frame_parser.match(image['fileName']).group(1)
			if int(frame_id) < 0 or int(frame_id) > 99:
				return annos
		except AttributeError as e:
			logger.error('unable to extract frame number of {0}'.format(image['fileName']))
			continue

		if annos.get(frame_id):
			logger.error('duplicate annotation for frame {0}'.format(image['fileName']))
			continue
		else:
			annos[frame_id] = {}
			anno = annos[frame_id]

		for label, infos in image['label'].items():
			if len(infos):
				for info in infos:
					track_name = label+'-'+str(info['num'])
					# ignores if the value for leave was 1
					if info['leave'] == 1:
						logger.info("{0} of {1} in lens-{2} is ignored for the value of leave is 1".format(track_name, frame_id, image_id))
						continue
					anno[track_name] = {
										'frame_id': frame_id,
										'track_id': info['num'], 
										'category': label, 
										'truncated': info['truncated'],
										'occluded': info['Occluded'],
										'overlapped': 0,	# False  
										'image_id': image_id,
										'bounding_box': (str(info['x1']), str(info['y1']), str(info['x2']), str(info['y2'])),
										}
	return annos

# ordered by frame index then lens orientation
def cluster_by_frames(image_set, lens_order=("center", "left", "right"), topk=None):
	frames_set = sorted(reduce(lambda x, y: x.update(y.keys()) or x, image_set, set()))[:topk]

	track_list = []	# each items containing one annotation
	for frame_id in frames_set:
		for lens_orient in lens_order:
			images = image_set[lens_orientation[lens_orient]]
			annos = images.get(frame_id)
			if not annos:
				continue

			# order by category then index
			track_names = sorted(annos.keys())
			for track_name in track_names:
				track_list.append(annos[track_name])			

	return track_list


# ordered by lens orientation then frame index
def cluster_by_lens(image_set, lens_order=("center", "left", "right"), topk=None):
	frames_set = sorted(reduce(lambda x, y: x.update(y.keys()) or x, image_set, set()))[:topk]

	track_list = []
	for lens_orient in lens_order:
			images = image_set[lens_orientation[lens_orient]]
			for frame_id in frames_set:
				annos = images.get(frame_id)
				if not annos:
					continue
			
				track_names = sorted(annos.keys())
				for track_name in track_names:
					track_list.append(annos[track_name])
	return track_list


#center, left, right = image_set
def format_output(track_list, f):
	for track_info in track_list:
		f.write('{frame_id} {track_id} {category} {truncated} {occluded} {overlapped} {image_id} {bounding_str}\n'.format(
			bounding_str=' '.join(track_info['bounding_box']), 
			**track_info))

def export_raw(db_result, title):
	name = os.path.join(DATA_DIR, 'triplelens', title+'_raw.txt')
	import json
	with open(name, 'w') as f:
		json.dump(db_result, f)


def main():
	config = parse_config()
	title = config.get('project', 'title')
	try:
		topk = config.getint('data', 'topk')
	except ValueError as e:
		topk = None

	db_result = fetch_annos(title)
	images = refine(db_result)
	output_filename = name_as_datetime(os.path.join(DATA_DIR,'triplelens'))
	with open(output_filename, 'w') as f:
		for image_set in images:
			track_list = cluster_by_frames(image_set, topk=topk)
			format_output(track_list, f)

def usage():
	return "exports data annotated for images captured by three lens together"
