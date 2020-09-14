import sys
import pandas as pd
sys.path.insert(1, './preprocessing/')
sys.path.insert(1, './normalisation/')
sys.path.insert(1, './integration/')

import main_preprocess
import main_normaliser
import main_integrator

# SETTINGS
path_input_file = '../../data/supplier_car.json'
path_target_file = '../../data/Target Data.xlsx'
path_xlsx_output = '../output/integrated_supplier_data.xlsx'

# read target dataframe
data_target = pd.read_excel(path_target_file)


# # call preprocessing
data_prepro = main_preprocess.main(path_input_file)
# data_prepro.to_csv('../output/preprocessing/preprocessing.csv')

# # call normalisation
data_norm = main_normaliser.normalise_dataframe(data_supplier=data_prepro, data_target=data_target)
# data_norm.to_csv('../output/normalisation/normalisation.csv')

# call integration
data_integr = main_integrator.integrate_datasets(
													data_norm=data_norm,
													data_target=data_target,
													path_xlsx_output=path_xlsx_output,
													integrator=None,
													df_prepro=data_prepro,
													df_norm=data_norm
												)

# data_integr.to_csv('../output/integration/integration.csv')