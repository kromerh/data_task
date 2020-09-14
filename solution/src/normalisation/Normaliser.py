import pandas as pd
pd.set_option('display.max_columns', 500)
import webcolors
import numpy as np
import re
from googletrans import Translator
import jellyfish
import geopandas
from geopy.geocoders import Nominatim


class Normaliser():

    def __init__(self, path_preprocessed_file, path_target_file):
        self.path_preprocessed_file = path_preprocessed_file # path to the preprocessed dataset
        self.path_target_file = path_target_file # path to the target dataset

    def load_preprocessed(self):
        """
        Loads the preprocessed data file into a pandas dataframe.
        INPUT:
            - None
        OUTPUT:
            - pandas dataframe
        """
        data = pd.read_csv(self.path_preprocessed_file, index_col=0)

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


    def normalise_color(self, dataframe, dataframe_target, dic_colors=None, verbose=False):
        """
        Normalisation of the BodyColorText column of the dataframe.
        Uses exact color matching, so the color has to be present in the target dataframe, otherwise it will be an "Other" color.
        For a probabilistic approach using the RGB space, see the ipynb file.

        The idea is to first see what colors we have in the target set and then define a mapping function to assign the respective
        colors to the colors in the input dataset.

        Assumption: The color attribute in the target data is the BodyColorText attribute in the input data. Must be confirmed with the client.
        INPUT:
            - dataframe: preprocessed dataset that is a pandas dataframe.
            - dataframe_target: target dataframe from the xls file
            - dic_colors: (optional) Is a dictionary that is the translation of the colors from German to English.
                            If not provided, a translator will be used.
            - verbose: If true, will print information if dic_colors was None or not
        OUTPUT:
            - dataframe: The input dataframe with the color column normalised.
        """

        # check inputs
        assert type(dataframe) == type(pd.DataFrame()), "Error in normalise_color! dataframe is not of type pd.DataFrame()"
        assert type(dataframe_target) == type(pd.DataFrame()), "Error in normalise_color! dataframe_target is not of type pd.DataFrame()"
        if dic_colors: assert type(dic_colors) == type({}), "Error in normalise_color! dic_color is not of type dictionary"
        assert 'BodyColorText' in dataframe.columns.tolist(), "Error in normalise_color! BodyColorText is not in the columns of the dataframe"
        assert 'color' in dataframe_target.columns.tolist(), "Error in normalise_color! color is not in the columns of the dataframe_target"

        # remove met
        dataframe['BodyColorText_new'] = dataframe['BodyColorText'].str.replace('mét.', '')
        # remove trailing whitespace
        dataframe['BodyColorText_new'] = dataframe['BodyColorText_new'].str.strip()

        # if no dictionary is provided, use a translator
        if dic_colors is None:
            if verbose: print('dic_colors is None')

            def translate_color(color):
                """
                Translates the color from German to English.
                Could be optimized by translating from any color into English.
                """
                translator = Translator()

                color_eng = translator.translate(color, src='de').text

                return color_eng

            colors = dataframe['BodyColorText_new'].unique()
            dic_colors = {} # translated colors

            for c in colors:
                dic_colors[c] = translate_color(c)


        # also make it all first letter uppercase
        dataframe['BodyColorText_trans'] = dataframe['BodyColorText_new'].apply(lambda x: dic_colors[x].capitalize() )

        # find exact matches of colors from the target dataframe
        def match_color(color, target_colors=[]):
            if color in target_colors:
                return color
            else:
                return 'Other'

        dataframe['color'] = dataframe['BodyColorText_trans'].apply(lambda x: match_color(x, dataframe_target['color'].unique().tolist()))

        return dataframe




    def normalise_make(self, dataframe, dataframe_target, threshold=0.879, verbose=False):
        """
        The idea is to compare the similarity between the words in the target dataset and the input dataset to match the car makers.
        For that I will use the Jaro-Winkler distance (JW score). It is best suited for short strings such as names with the goal of comparing these two names.
        It compares mathematically the number of matching characters and the sequence order. A value close to 0 indicates not similar at all,
        and 1 indicates an exact match.
        INPUT:
            - dataframe: preprocessed dataset that is a pandas dataframe.
            - dataframe_target: target dataframe from the xls file
            - threshold: Threshold below which the JW score will result in the make attribute being classified as "Other"
            - verbose: If true, will print information for which make attributes the JW score was below threshold
        OUTPUT:
            - dataframe: The input dataframe with the make column normalised.
        """
        # check inputs
        assert type(dataframe) == type(pd.DataFrame()), "Error in normalise_make! dataframe is not of type pd.DataFrame()"
        assert type(dataframe_target) == type(pd.DataFrame()), "Error in normalise_make! dataframe_target is not of type pd.DataFrame()"
        assert type(threshold) == type(0.785), f"Error in normalise_make! threshold is not of type {type(0.785)}"
        assert 'MakeText' in dataframe.columns.tolist(), "Error in normalise_make! MakeText is not in the columns of the dataframe"
        assert 'make' in dataframe_target.columns.tolist(), "Error in normalise_make! make is not in the columns of the dataframe_target"


        makers_input = pd.Series(dataframe['MakeText'].unique()) # makers in the input file
        # makers in target file
        makers_target = pd.Series(dataframe_target['make'].unique().tolist())
        makers_target = makers_target.dropna() # drop the nan
        makers_target_lowercase = makers_target.str.lower()

        # convert to dataframe for easier comparison
        df_makers = pd.DataFrame(makers_input, columns=['makers_input'])


        def compare_makers(row, makers_target, makers_target_lowercase, threshold, verbose=False):
            # make input lowercase
            s = row.lower()
            # calculate jaro-winkler score between the lowercase strings
            jw_scores = makers_target_lowercase.apply(lambda x: jellyfish.jaro_winkler(s, x))
            idx_max = np.argmax(jw_scores) # maximal score index
            score_max = jw_scores.iloc[idx_max]
            best_match = makers_target.iloc[idx_max]
            if score_max < threshold:
                if verbose: print(f"For input {row}, the best match was {best_match} with a JW score of {score_max}.")

            return pd.Series([row, best_match, score_max], index=['maker_input', 'best_match', 'JW score'])

        df_maker_match = df_makers['makers_input'].apply(lambda row: compare_makers(row, makers_target, makers_target_lowercase, threshold, verbose))

        # replace values with below the score with "Other"
        df_maker_match.loc[:, 'best_match'][df_maker_match['JW score'] < threshold] = 'Other'

        # map the dataframe to the input dataframe as a lookup table
        dataframe['make'] = dataframe['MakeText'].apply(lambda x: df_maker_match[ df_maker_match['maker_input'] == x].loc[:,'best_match'].values[0])

        return dataframe


    def get_country_from_city(self, dataframe):
        """
        Uses geopandas to get the country for the city. If one than more address for a city is found there will be an error.
        INPUT:
            - dataframe: pandas dataframe that must contain a city column
        OUTPUT:
            - pandas dataframe with the country that the city is in
        """
        assert type(dataframe) == type(pd.DataFrame()), "Dataframe is not a pd.DataFrame()!"
        assert 'City' in dataframe.columns, "City is not a columns in the dataframe!"

        df_city = pd.DataFrame(dataframe['City'].unique(), columns=['City'])

        def get_country(city):
            r = geopandas.tools.geocode(city, provider='nominatim', user_agent='autogis_xx', timeout=4) # get address
            assert r.shape[0] == 1, "More than one address for that city!" # make sure only one city
            long, lat = r['geometry'].x.values[0], r['geometry'].y.values[0] # get long and lat
            locator = Nominatim(user_agent="myGeocoder")
            coordinates = f"{lat}, {long}"
            location = locator.reverse(coordinates) # get location information
            country = location.raw['address']['country_code'] # return country code
            return country.upper()

        df_city['Country'] = df_city['City'].apply(lambda x: get_country(x))

        dataframe['Country'] = dataframe['City'].apply(lambda x: df_city[ df_city['City'] == x ].loc[:, 'Country'].values[0])

        return dataframe