import pandas as pd
import getopt
import sys

from Preprocessor import Preprocessor

# some settings for the preprocessing
COLS_TO_KEEP = ['MakeText', 'TypeName', 'ModelText', 'ModelTypeText'] # columns to add to the dataframe after pivoting
DO_MISSING = False # print missing values information
PLOT_MISSING_VALUES = False # plot missing values
COL_ORDER = ['BodyTypeText', 'BodyColorText', 'ConditionTypeText', 'City',
'MakeText', 'ModelText', 'ModelTypeText', 'DriveTypeText', 'TransmissionTypeText','FirstRegMonth', 'FirstRegYear', 'Km'] # change order of columns






def main(path_input_file, path_output_file=None):
	# call object
	pre = Preprocessor(path_input_file=path_input_file)

	# load dataframe
	data_in = pre.load_input_json()

	if DO_MISSING:
		print(f"Missing values in the input dataframe:")
		# show missing values (optional)
		data_missing = pre.show_missing_values(data_in, plot=PLOT_MISSING_VALUES)
		print(data_missing)

	# group by id and pivot the table
	data_in_pivot = pre.groupby_id_and_pivot(data_in, cols_to_keep=COLS_TO_KEEP)

	# re-order dataframe columns for visibility
	data_ordered = pre.order_columns(data_in_pivot, col_order=COL_ORDER)


	# write output csv file or return dataframe
	if path_output_file is not None:
		data_ordered.to_csv(path_output_file, index=True)
	else:
		return data_ordered





if __name__ == '__main__':
	# Get the arguments from the command-line except the filename
	argv = sys.argv[1:]

	try:
		if len(argv) == 2:
			path_input_file = argv[0]
			output_file = argv[1]
			main(path_input_file, output_file)
		elif len(argv) == 1:
			path_input_file = argv[0]
			main(path_input_file)
		else:
			print('Error! usage: main_preprocess.py path_input_file (optional: path_output_file)')
			sys.exit(2)

	except getopt.GetoptError:
		# Print something useful
		print('Error! usage: main_preprocess.py path_input_file (optional: path_output_file)')

		sys.exit(2)