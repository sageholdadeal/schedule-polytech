from sys import argv
import argparse

from transformator import Transformer


def load_table_size_param(param_name, param_index):
	value = None
	if len(argv) > param_index:
		value = argv[param_index]
		if value == 'auto':
			return value
		try:
			value = int(value)
		except ValueError:
			print('Argument \'%s\' should be an integer' % param_name)
	return value


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('filename', type=str)
	parser.add_argument('font_path', type=str)
	parser.add_argument('--rows', default=None, type=int)
	parser.add_argument('--cols', default=None, type=int)
	args = parser.parse_args()

	try:
		t = Transformer(args.font_path)
	except FileNotFoundError:
		print('font file not found')
		return 2

	try:
		f = open(args.filename, "rb")
		t.transform(f.read(), args.rows, args.cols)
	except FileNotFoundError:
		print('File %s doesn\'t exist' % args.filename)
		return 1
	return 0
