# -*- coding: utf-8 -*-
import os
import shutil

from core.mail import NotifyMailSender
from utils.stocking import fetch_annos
from utils.parse import parse_config
from settings import logger


# clean the result got from database, only leave necessary fields
# a bug now in website leads 1936*1456 => 752*448
def refine(db_result):

	def annotated_label_region(labels):
		for label, annotations in labels.items():
			if len(annotations) == 1:
				anno = annotations[0]
				#return label, (anno['x1']*2.57, anno['y1']*3.25, anno['x2']*2.57, anno['y2']*3.25)
				return label, (anno['x1'], anno['y1'], anno['x2'], anno['y2'])
			elif len(annotations) == 0:
				pass
			else:
				logger.error('more than 1 markers was annotated for {0}'.format(label))	
				return

	clean_result = {}
	for record in db_result:
		record = record['rdata']
		clean_result[record['title']] = {}
		images = clean_result[record['title']]
		for img in record['images']:
			frame = img['fileName'].split("%5C")[-1]
			if frame.endswith('.jpg') and frame.startswith('frame'):
				frame = frame.replace('.jpg', '.png')
				images[frame] = {}
			else:
				logger.error("filename {0} is invalid".format(img['fileName']))


			label, region = annotated_label_region(img['label'])
			images[frame]['label'] = label
			images[frame]['region'] = region

	return clean_result


# interface, 
def process(root_path, results):
	for label_dir in os.listdir(root_path):
		# if not label_dir.endswith('OOO'):		# FILTER: used when last processing failed
		# 	continue
		full_label_dir = os.path.join(root_path, label_dir)
		if not os.path.isdir(full_label_dir):
			continue
		for title in os.listdir(full_label_dir):
			current_dir = os.path.join(full_label_dir, title)
			if not os.path.isdir(current_dir):
				continue
			# frame_num = int(title.split('_')[-1])		# FILTER
			# if frame_num < 17226:
			# 	continue
			anno = results.get(title)
			if anno:
				generate_anno_text(current_dir, anno)
				crop_all_imgs(current_dir, anno)
			else:
				logger.error("unable to find corresponding annotation for {0}".format(title))

# crops images in the path as region described in anno
def crop_all_imgs(path, anno):
	title = os.path.basename(path)
	# cropped_path = os.path.join(path, title+'_cropped')
	cropped_path = os.path.join(path, 'cropped')
	# new_name =  os.path.join(path, 'cropped')
	# shutil.move(cropped_path, new_name)

	images = filter(lambda x: x.endswith('.png'), os.listdir(path))
	if not os.path.exists(cropped_path):
		os.makedirs(cropped_path)

	from utils.crop import crop
	for frame in images:
		img_name = os.path.join(path, frame)
		dst_name = os.path.join(cropped_path, frame)
		region = anno[frame]['region']
		# if os.path.exists(dst_name):
		# 	continue
		try:
			crop(img_name, dst_name, region)
		except Exception as e:
			region_str = ','.join(map(lambda x: str(int((x))), region))
			logger.error('error occured when cropping {0} with region {1}'.format(img_name, region_str))


# generates the annotation text to indicate regions and labels
def generate_anno_text(path, anno):
	display_anno = []
	for frame, info in anno.items():
		# anno_info = [frame, ','.join(map(lambda x: str(int((x))), info['region'])), info['label']]
		anno_info = [frame, ','.join(map(lambda x: str(int((x))), info['region']))]
		display_anno.append(anno_info)
	display_anno = sorted(display_anno, key=lambda x: x[0], reverse=False)

	title = os.path.basename(path)
	anno_text_name = os.path.join(path, title+'.txt')
	with open(anno_text_name, 'w') as f:
		for i, line in enumerate(display_anno, start=1):
			line.insert(0, str(i))
			f.write(' '.join(line) + '\n')


def main():
	config = parse_config()
	title = config.get('project', 'title')
	data = config.get('project', 'data').decode(settings.DEFAULE_DECODING)
	recipients = config.get('project', 'email')

	db_result = fetch_annos(title)
	refine_result = refine(db_result)
	for dirname in os.listdir(data):
		path = os.path.join(data, dirname)
		if os.path.isdir(path):
			process(path, refine_result)

	if recipients:
		NotifyMailSender(recipients).notify(title)


