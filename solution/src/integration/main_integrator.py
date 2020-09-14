import pandas as pd
import getopt
import sys

from Integrator import Integrator



def integrate_datasets(data_norm, data_target, path_xlsx_output, integrator=None, df_prepro=None, df_norm=None):
	"""
	Integrates the supplier dataset into the target schema.
	INPUT:
		- data_norm: preprocessed and normalised supplier dataset, must be in wide format
		- data_target: target dataset
		- path_xlsx_output: full path where to save the final xlsx file
	OUTPUT:
		- pandas dataframe
	"""
	if integrator is None:
		integrator = Integrator(
				path_normalised_file=None,
				path_target_file=None,
				path_prepro_file=None,
				path_xlsx_output=path_xlsx_output,
				path_integr_output=None
			)

	# renames the columns in the normalised dataframe so they can be appended to the target dataframe
	data = integrator.rename_columns(data_norm)

	# drops the columns in the normalised dataframe that have no match in the target dataframe
	data = integrator.drop_columns(data, data_target)

	# appends the supplier dataset to the target dataset
	data = integrator.append_supplier_to_target(data, data_target)

	# saves all the files in this task in one single xlsx file with each step in a different sheet
	integrator.save_xlsx(data, df_prepro=df_prepro, df_norm=df_norm)

	return data





def main(path_normalised_file, path_target_file, path_prepro_file, path_xlsx_output, path_integr_output=None):
	# call object
	integr = Integrator(
			path_normalised_file=path_normalised_file,
			path_target_file=path_target_file,
			path_prepro_file=path_prepro_file,
			path_xlsx_output=path_xlsx_output,
			path_integr_output=path_integr_output
		)

	# load input dataframe
	data = integr.load_normalised()

	# load target dataframe
	data_target = integr.load_target()

	data = integrate_datasets(data_norm=data, data_target=data_target, path_xlsx_output=path_xlsx_output, integrator=integr)

	# write output csv file
	if path_integr_output: data.to_csv(path_integr_output, index=True)

if __name__ == '__main__':
	# Get the arguments from the command-line except the filename
	argv = sys.argv[1:]

	try:
		if len(argv) == 5:
			path_normalised_file = argv[0]
			path_target_file = argv[1]
			path_prepro_file = argv[2]
			path_xlsx_output = argv[3]
			path_integr_output = argv[4]
			main(path_normalised_file, path_target_file, path_prepro_file, path_xlsx_output, path_integr_output)
		elif len(argv) == 4:
			path_normalised_file = argv[0]
			path_target_file = argv[1]
			path_prepro_file = argv[2]
			path_xlsx_output = argv[3]
			main(path_normalised_file, path_target_file, path_prepro_file, path_xlsx_output)
		else:
			print('Error! usage: main_integrator.py path_normalised_file path_target_file path_prepro_file path_xlsx_output (optional: path_integr_output)')
			sys.exit(2)


	except getopt.GetoptError:
		# Print something useful
		print('Error! usage: main_integrator.py path_normalised_file path_target_file path_prepro_file path_xlsx_output (optional: path_integr_output)')


		sys.exit(2)