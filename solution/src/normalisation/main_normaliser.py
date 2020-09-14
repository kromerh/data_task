import pandas as pd
import getopt
import sys

from Normaliser import Normaliser

# some settings for the normalisation
# use when the API call reports too many calls, toggle lines 44 and 47
dic_colors = {'anthrazit': 'anthracite',
 'beige': 'beige',
 'blau': 'blue',
 'bordeaux': 'bordeaux',
 'braun': 'brown',
 'gelb': 'yellow',
 'gold': 'gold',
 'grau': 'Gray',
 'grün': 'green',
 'orange': 'orange',
 'rot': 'red',
 'schwarz': 'black',
 'silber': 'silver',
 'violett': 'violet',
 'weiss': 'White'}

# threshold to classify make as "Other" based on JW distance
THRESHOLD_NORMALISE_MAKE = 0.879

# verboses for testing
VERBOSE_NORMALISE_MAKE = False
VERBOSE_NORMALISE_COLOR = False

def normalise_dataframe(data_supplier, data_target):
	"""
	Normalises the supplier dataset.
	INPUT:
		- data_supplier: preprocessed supplier dataset, must be in wide format
		- data_target: target dataset
	OUTPUT:
		- pandas dataframe
	"""

	norm = Normaliser(path_preprocessed_file=None, path_target_file=None)

	# normalise color: if google API does not work
	# data_supplier = norm.normalise_color(data_supplier, data_target, dic_colors=dic_colors, verbose=VERBOSE_NORMALISE_COLOR)

	# normalise color: if google API does work
	data_supplier = norm.normalise_color(data_supplier, data_target, dic_colors=None, verbose=VERBOSE_NORMALISE_COLOR)

	# normalise make
	data_supplier = norm.normalise_make(data_supplier, data_target, threshold=THRESHOLD_NORMALISE_MAKE, verbose=VERBOSE_NORMALISE_MAKE)

	# get country from city
	data_supplier = norm.get_country_from_city(data_supplier)

	return data_supplier


def main(path_preprocessed_file, path_target_file, path_output_file=None):
	# call object
	norm = Normaliser(path_preprocessed_file=path_preprocessed_file, path_target_file=path_target_file)

	# load input dataframe
	data = norm.load_preprocessed()

	# load target dataframe
	data_target = norm.load_target()

	data = normalise_dataframe(data, data_target)

	# write output csv file or return the dataframe
	if path_output_file is not None:
		data.to_csv(path_output_file, index=True)

if __name__ == '__main__':
	# Get the arguments from the command-line except the filename
	argv = sys.argv[1:]

	try:
		if len(argv) == 3:
			path_preprocessed_file = argv[0]
			path_target_file = argv[1]
			path_output_file = argv[2]
			main(path_preprocessed_file, path_target_file, path_output_file)
		elif len(argv) == 2:
			path_preprocessed_file = argv[0]
			path_target_file = argv[1]
			main(path_preprocessed_file, path_target_file)
		else:
			print('Error! usage: main_normaliser.py path_preprocessed_file path_target_file (optional: path_output_file)')
			sys.exit(2)

	except getopt.GetoptError:
		# Print something useful
		print('Error! usage: main_normaliser.py path_preprocessed_file path_target_file (optional: path_output_file)')

		sys.exit(2)