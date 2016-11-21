import os
import pickle
import jieba
from utils.parse import parse_config
from utils.dateutil import name_as_datetime
import settings

def term_count(content):
	frequency_table = {}

	for line in content:
		seg_list = jieba.cut(line, cut_all=True)
		for seg in seg_list:
			if not frequency_table.get(seg):
				frequency_table[seg] = 0
			frequency_table[seg] += 1

	return frequency_table

def inverse_document_freq(complete, subset):
	idf = {}
	for k, v in subset.items():
		if v < 3:
			continue
		idf[k] = float(v) / complete.get(k, -1)

	return idf

def export(table, filename):
	table = sorted(table.items(), key=lambda x: x[1], reverse=True)
	with open(filename, 'w') as f:
		for k, v in table:
			f.write('{0}\n'.format(k))


def sent_rank(content, freq_table, scaledown):
	rank_table = {}
	for line in content:
		rank = 0
		seg_list = jieba.cut(line, cut_all=True)
		for i, seg in enumerate(seg_list, start=1):
			rank += freq_table.get(seg, 0)
		rank_table[line.strip()] = rank * 1.0 / (i + scaledown)

	return rank_table


def stat(predict_sent, result_sent, source_sent):
	result_sent = { k: 1 for k in result_sent }

	hit = 0	# true positive
	for k in predict_sent.keys():
		if result_sent.get(k):
			hit += 1


	miss = 0 # false negative
	for k in result_sent.keys():
		if not predict_sent.get(k):
			miss += 1

	tp = hit
	fp = len(predict_sent) - hit
	fn = miss
	tn = len(source_sent) - len(predict_sent) - miss

	print("========================STATISTICS=========================")
	print("True Positive: {0}\tFalse Positive: {1}".format(tp, fp))
	print("False Negative: {0}\tTrue Negative: {1}".format(fn, tn))
	print("Precision: {0}".format(1.0 * tp/(tp + fp)))
	print("Recall: {0}".format(1.0 * tp/(tp + fn)))
	print("Accuracy: {0}".format(1.0 * (tp + tn)/(tp + tn + fp + fn)))


def predict(source, idf, topk, scaledown):
	rank_table = sent_rank(source, idf, scaledown)
	num = int(len(rank_table) * topk)
	topk_sentence = sorted(rank_table.items(), key=lambda x: x[1], reverse=True)[:num]
	result = { k: v for k, v in topk_sentence }
	return result


def rank_distribution(sent_with_score, N=10):
	max_score = max(sent_with_score.values())
	min_score = min(sent_with_score.values())
	
	step_width = (max_score-min_score) / N
	distribution = [ 0 for i in range(N) ]

	def get_rank_by_score(score):
		rank = 1
		while rank <= N:
			if score <= min_score + step_width * rank:
				return rank - 1	# starts from 0
			else:
				rank += 1
		return N - 1

	for sent, score in sent_with_score.items():
		rank = get_rank_by_score(score)
		distribution[rank] += 1

	print("{0:.3} <---------------------------------> {1:.3}".format(min_score, max_score))
	print("    {0}    ".format(distribution))

	return distribution


def loads_dict(filename):
	container={}
	with open(filename, 'r') as f:
		for line in f:
			container[line.strip()] = 1
	return container

def loads_list(filename):
	container = []
	with open(filename, 'r') as f:
		for line in f:
			container.append(line.strip())
	return container

def collect(root, files):
	content = []
	for filename in files:
		content.extend(loads_list(os.path.join(root, filename)))
	return content


def main():
	config = parse_config()
	train_root = config.get('train', 'root')
	train_sources = config.get('train', 'source').split(',')
	train_results = config.get('train', 'result').split(',')
	model = os.path.join(train_root, config.get('train', 'model'))

	test_root = config.get('test', 'root')
	test_sources = config.get('test', 'source').split(',')
	test_results = config.get('test', 'result').split(',')

	predict_root = config.get('predict', 'root')
	data = config.get('predict', 'data').split(',')

	scaledown = config.getint('parameters', 'scaledown')
	topk = config.getfloat('parameters', 'topk')
	
	# get model from data or the dumped one
	if config.getboolean('train', 'train'):
		source_tf = term_count(collect(train_root, train_sources))
		result_tf = term_count(collect(train_root, train_results))
		idf = inverse_document_freq(source_tf, result_tf)
		if config.getboolean('train', 'save'):
			with open(model, 'wb') as f:
				pickle.dump(idf, f)
	else:
		with open(model, 'rb') as f:
			idf = pickle.load(f)

	if config.getboolean('test', 'stat'):
		test_source = collect(test_root, test_sources)
		test_result = collect(test_root, test_results)
		predict_result = predict(test_source, idf, topk, scaledown)
		stat(predict_result, test_result, test_source)

		rank_distribution(predict_result)

		rank_distribution(predict(test_result, idf, 1, scaledown))

		# real_distribution = rank_distribution(predict_result, test_result)
		# predict_distribution = rank_distribution(predict_result, predict_result)

		# for r, p in zip(real_distribution, predict_distribution):
		# 	if p == 0:
		# 		print 0
		# 	else:
		# 		print r*1.0/p


	if config.getboolean('predict', 'export'):
		product_dir = os.path.join(settings.DATA_DIR, 'termfreq')
		predict_data = collect(predict_root, data)
		export(predict(predict_data, idf, topk, scaledown), name_as_datetime(product_dir))



def usage():
	return "counts terms in a complete-set and a subset, to find out features in the subset"