import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


class Preprocessor():

    def __init__(self, path_input_file):
        self.path_input_file = path_input_file # path to the input json file

    def load_input_json(self):
        """
        Loads the input json file into a pandas dataframe.
        INPUT:
            - None
        OUTPUT:
            - pandas dataframe
        """
        assert self.path_input_file.endswith('.json'), f"Error in load_input_json, input filename does not end with .json"
        data_in = pd.read_json(self.path_input_file, lines=True)


        return data_in


    def show_missing_values(self, dataframe, plot=False):
        """
        Displays the missing values.
        INPUT:
            - dataframe: pandas dataframe to check for missing values
            - plot: flag that if True will produce a plot of the missing values
        OUTPUT:
            - pandas dataframe with missing values per column
            - seaborn plot if the plot flag was true
        """
        assert type(dataframe) == type(pd.DataFrame()), f"Error in show_missing_values, input dataframe is of type {type(dataframe)}, must be pd.DataFrame"
        percent_missing = dataframe.isnull().sum() * 100 / len(dataframe)
        missing_value_df = pd.DataFrame({'column_name': dataframe.columns,
                                         'percent_missing': percent_missing})
        if plot:
            sns.heatmap(dataframe.isnull(), yticklabels=False, cbar=False, cmap='Reds')
            plt.title(f'Missing values in the dataframe per column (more red, more missing)')
            plt.tight_layout()
            plt.show()

        return missing_value_df


    def groupby_id_and_pivot(self, dataframe, cols_to_keep=[]):
        """
        Takes as input the dataframe and returns the pivoted version (Attribute Names) of it.
        Other columns from the original dataframe will be kept if specified.
        INPUT:
            - dataframe: pandas dataframe to be pivoted
            - cols_to_keep: list of the columns of the original, unpivoted dataframe to keep, e.g. the MakeText
        OUTPUT:
            - pandas dataframe that is pivoted version of the original dataframe with the cols that should be kept
        """

        def pivot_data(dataframe, cols_to_keep=[]):
            """
            Takes as input the dataframe grouped by ID (which is one input) and returns the pivoted version (Attribute Names) of it.
            Other columns from the original dataframe will be kept if specified.
            INPUT:
                - dataframe: pandas dataframe to be pivoted
                - cols_to_keep: list of the columns of the original, unpivoted dataframe to keep, e.g. the MakeText
            OUTPUT:
                - pandas dataframe that is pivoted version of the original grouped dataframe with the cols that should be kept
            """
            df_out = dataframe.pivot_table(values='Attribute Values', index=['ID'],columns=['Attribute Names'],aggfunc='first')
            for c in cols_to_keep:
                assert len(dataframe[c].unique()) == 1, f"Length of unique entries is not the same for column {c} {print(dataframe[c].unique())}"
                df_out[c] = dataframe[c].values[0]

            return df_out


        data_in_pivot = dataframe.groupby('ID').apply(lambda x: pivot_data(x, cols_to_keep=cols_to_keep))
        data_in_pivot = data_in_pivot.droplevel(0) # drop multiindex

        return data_in_pivot



    def order_columns(self, dataframe, col_order=[]):
        """
        Takes as input a dataframe and arranges the order of columns as specified. Remaining columns will be added.
        If column not in the dataframe, do nothing.
        INPUT:
            - dataframe: pandas dataframe
            - col_order: list of the columns in the dataframe that should be reordered.
        OUTPUT:
            - pandas dataframe with new order
        """
        data_out = pd.DataFrame()
        for new_col in col_order:
            if new_col in dataframe.columns: data_out[new_col] = dataframe[new_col]
        for c in dataframe.columns:
            if c not in data_out.columns:
                data_out.loc[:, c] = dataframe.loc[:, c]
        assert len(data_out.columns) == len(dataframe.columns), 'Length of resorted columns is not the same!'

        return data_out
