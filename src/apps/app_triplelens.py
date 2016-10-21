# -*- coding: utf-8 -*-
import os
import re
import sys

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

		# FILTER: only first 18 frames was annotated for now
		annoted_frames = sorted(center.keys())[:18]
		center = subset(center, annoted_frames)
		left = subset(left, annoted_frames)
		right = subset(right, annoted_frames)

		detect_overlapped(center, [left, right])
		detect_overlapped(left, [center, right])
		
		images.extend([center, left, right])

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
	frame_parser = re.compile('.+/image(\d+).jpg')

	for image in images:
		try:
			frame_id = frame_parser.match(image['fileName']).group(1)
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
					anno[track_name] = {'track_id': info['num'], 
										'category': label, 
										'truncated': info['truncated'],
										'occluded': info['Occluded'],
										'overlapped': 0,	# False  
										'image_id': image_id,
										'bounding_box': (str(info['x1']), str(info['y1']), str(info['x2']), str(info['y2'])),
										}


	return annos

def format_output(images, f):
	annoted_frames = sorted(images.keys())[:18]

	for frame_id in annoted_frames:
		annos = images[frame_id]
		track_names = sorted(annos.keys())
		for track_name in track_names:
			track_info = annos[track_name]
		# for track_name, track_info in annos.items():
			f.write('{frame_id} {track_id} {category} {truncated} {occluded} {overlapped} {image_id} {bounding_str}\n'.format(
				frame_id=frame_id, 
				bounding_str=' '.join(track_info['bounding_box']), 
				**track_info))


def main():
	config = parse_config()
	title = config.get('project', 'title')

	db_result = fetch_annos(title)
	images = refine(db_result)
	output_filename = name_as_datetime(os.path.join(DATA_DIR,'triplelens'))
	with open(output_filename, 'w') as f:
		for image in images:
			format_output(image, f)

if __name__ == '__main__':
	main()
