import pandas as pd
pd.set_option('display.max_columns', 500)
import xlsxwriter
import sys

# new name fr the columns in the normalised dataframe to be mapped to the target schema
DIC_COLS_RENAME = {
            'BodyTypeText': "carType",               # assumed normalized
            'ConditionTypeText': "condition",        # assumed normalized
            'City': 'city',
            'ModelText': 'model',                    # assumed normalized
            'ModelTypeText': 'model_variant',        # assumed normalized
            'Km': 'mileage',                         # assumed normalized
            'Country': 'country'
            }




class Integrator():

    def __init__(self, path_normalised_file, path_target_file, path_prepro_file, path_xlsx_output, path_integr_output):
        self.path_normalised_file = path_normalised_file # path to the normalised dataset
        self.path_target_file = path_target_file # path to the target dataset
        self.path_prepro_file = path_prepro_file # path to the preprocessed datafrile
        self.path_xlsx_output = path_xlsx_output # path where the final output xlsx will be stored
        self.path_integr_output = path_integr_output # path where csv of the integrator will be stored, only for internal processing and debugging

    def load_normalised(self):
        """
        Loads the nomralised data file into a pandas dataframe.
        INPUT:
            - None
        OUTPUT:
            - pandas dataframe
        """
        data = pd.read_csv(self.path_normalised_file, index_col=0)

        return data


    def load_target(self):
        """
        Loads the target data xls file into a pandas dataframe.
        INPUT:
            - None
        OUTPUT:
            - pandas dataframe
        """
        data = pd.read_excel(self.path_target_file)

        return data


    def rename_columns(self, data, dic_cols_rename=DIC_COLS_RENAME):
        """
        Renames the columns in the normalised dataframe so they can be appended to the target dataframe.
        INPUT:
            - data: pandas dataframe that is the normalised dataframe
            - dic_cols_rename: dictionary with the mapping between the columns to be renamed
        OUTPUT:
            - pandas dataframe with the renamed columns
        """
        for k in dic_cols_rename.keys():
            assert k in data.columns, f"Error in rename_columns! Column {k} is not in the columns if the dataframe which are {data.columns.tolist()}."

        data = data.rename(dic_cols_rename, axis=1)

        return data


    def drop_columns(self, data, data_tar):
        """
        Drops the columns in the normalised dataframe that have no match in the target dataframe.
        INPUT:
            - data: pandas dataframe that is the normalised dataframe
            - data_tar: target dataframe, any column in data that is not in data_tar will be dropped from data
        OUTPUT:
            - pandas dataframe of supplier data with the dropped columns
        """

        # get list of columns to drop
        cols_to_drop = []
        for col in data.columns:
            if col not in data_tar.columns:
                cols_to_drop.append(col)

        data = data.drop(columns=cols_to_drop)

        return data


    def append_supplier_to_target(self, data, data_tar):
        """
        Appends the supplier dataset to the target dataset.
        INPUT:
            - data: pandas dataframe that is the normalised dataframe with columns matching those to the target dataset
            - data_tar: target dataframe, any column in data that is not in data_tar will be dropped from data
        OUTPUT:
            - pandas dataframe of supplier data appended to target data
        """
        for k in data.columns:
            assert k in data_tar.columns, f"Error in append_supplier_to_target! Column {k} of processed supplier dataset is not in the target dataset."

        data = data.reset_index(drop=True) # reset the ID index

        # append the data
        data = data_tar.append(data, ignore_index=True)

        # replace NaN with 'null' to have consistency with target dataset
        data = data.fillna('null')

        return data


    def save_xlsx(self, data, df_prepro=None, df_norm=None):
        """
        Saves all the files in this task in one single xlsx file with each step in a different sheet.
        INPUT:
            - data: pandas dataframe that is the normalised dataframe
            - data_tar: target dataframe, any column in data that is not in data_tar will be dropped from data
        OUTPUT:
            - creates an xls file in the location
        """

        if self.path_prepro_file is not None:
            # load preprocessed file
            df_prepro = pd.read_csv(self.path_prepro_file, index_col=0)

        if self.path_normalised_file is not None:
            # load normalised file
            df_norm = pd.read_csv(self.path_normalised_file, index_col=0)



        # combined datafile
        df_comb = data

        def apply_autofilter(writer, n_rows, n_cols, sheet_name):
            """
            Applies an autofilter to the columns based on the sheetname.
            """
            # Get the xlsxwriter objects from the dataframe writer object.
            workbook  = writer.book
            worksheet = writer.sheets[sheet_name]
            # Apply the autofilter based on the dimensions of the dataframe.
            worksheet.autofilter(0, 0, n_rows, n_cols)


        with pd.ExcelWriter(self.path_xlsx_output, engine = 'xlsxwriter') as writer:
            sheet_name = 'Pre-processing'
            df_prepro.to_excel(writer, sheet_name=sheet_name)
            n_rows, n_cols = df_prepro.shape[0], df_prepro.shape[1]
            apply_autofilter(writer, n_rows, n_cols, sheet_name)

            sheet_name = 'Normalisation'
            df_norm.to_excel(writer, sheet_name=sheet_name)
            n_rows, n_cols = df_norm.shape[0], df_norm.shape[1]
            apply_autofilter(writer, n_rows, n_cols, sheet_name)

            sheet_name = 'Integration'
            df_comb.to_excel(writer, sheet_name=sheet_name, index=None)
            n_rows, n_cols = df_comb.shape[0], df_comb.shape[1]
            apply_autofilter(writer, n_rows, n_cols, sheet_name)

        return None