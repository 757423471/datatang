import os
import jieba
from utils.parse import parse_config
from utils.dateutil import name_as_datetime
import settings

def term_count(filename):
	frequency_table = {}

	with open(filename, 'r') as f:
		for line in f:
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


def sent_rank(filename, freq_table, scaledown):
	rank_table = {}
	with open(filename, 'r') as f:
		for line in f:
			rank = 0
			seg_list = jieba.cut(line, cut_all=True)
			for i, seg in enumerate(seg_list, start=1):
				rank += freq_table.get(seg, 0)
			rank_table[line.strip()] = rank * 1.0 / (i + scaledown)

	return rank_table


def stat(predict_sent, result_sent, total):
	tp = fp = 0	# true positive and false positive
	for k in predict_sent.keys():
		if result_sent.get(k):
			tp += 1
		else:
			fp += 1

	fn = 0 # false negative
	for k in result_sent.keys():
		if not predict_sent.get(k):
			fn += 1

	print("========================STATISTICS=========================")
	print("True Positive: {0}\tFalse Positive: {1}".format(tp, fp))
	print("False Negative: {0}\tTrue Negative: {1}".format(fn, total-fn))
	print("Precision: {0}".format(1.0*tp/(tp + fp)))
	print("Recall: {0}".format(1.0*tp/(tp + fn)))


def predict(source, idf, topk, scaledown):
	rank_table = sent_rank(source, idf, scaledown)
	num = int(len(rank_table) * topk)
	topk_sentence = sorted(rank_table.items(), key=lambda x: x[1], reverse=True)[:num]
	result = { k: v for k, v in topk_sentence }
	return result

def loads(filename):
	container={}
	with open(filename, 'r') as f:
		for line in f:
			container[line.strip()] = 1
	return container

def main():
	config = parse_config()
	train_source = config.get('train', 'source')
	train_result = config.get('train', 'result')
	test_source = config.get('test', 'source')
	test_result = config.get('test', 'result')
	predict_source = config.get('predict', 'source')

	scaledown = config.getint('parameters', 'scaledown')
	topk = config.getfloat('parameters', 'topk')

	source_tf = term_count(train_source)
	result_tf = term_count(train_result)
	idf = inverse_document_freq(source_tf, result_tf)
	stat(predict(test_source, idf, topk, scaledown), loads(test_result), len(loads(test_source)))
	
	product_dir = os.path.join(settings.DATA_DIR, 'termfreq')

	if config.getboolean('parameters', 'export'):
		export(predict(predict_source, idf, topk, scaledown), name_as_datetime(product_dir))



def usage():
	return "counts terms in a complete-set and a subset, to find out features in the subset"