# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 18:07:02 2017

@author: MZD
"""

import pandas as pd
pd.options.mode.chained_assignment = 'raise'
import os
from collections import OrderedDict
import json
import logging
import control_parameters
from balsa.matrices import to_fortran, read_fortran_rectangle
import EarlyValid as ev

def setupLogger(model_name, logname):
    # remove pre existing log
    # if os.path.exists(os.path.join(control_parameters.inputDirListing, logname)):
        # os.remove(os.path.join(control_parameters.inputDirListing, logname))

    logger = logging.getLogger(model_name)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(os.path.join(control_parameters.inputDirListing, logname))
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s"))
    logger.addHandler(fh)

    return logger


# function to concatenate two dfs
def concat_df(df1, df2, num):

    """
    A function to concatenate two dataframes by columns
    :param df1: dataframe 1
    :param df2: dataframe 2
    :param num: 0 for row and 1 for column
    :return concatenated df
    """
    # once sampled, now concatenate the information back to the household dataframe
    df1.reset_index(drop=True, inplace=True)
    df2.reset_index(drop=True, inplace=True)
    df1 = df1.loc[:,~df1.columns.duplicated()]
    df2 = df2.loc[:,~df2.columns.duplicated()]
    df1 = pd.concat([df1, df2], axis=num)

    return df1

def market_segment(df):

    """
    This function takes a dataframe and assigns the market segment to it that is used in the GGHM.
    :param df: dataframe that needs to be assigned the market segment
    :return df: with market segment attached
    :raises KeyError: some columns are missing in order to undertake the market segment calculation

    """
    if {'hhinc', 'auto_suff'}.issubset(df.columns):
        # create segments
        df.loc[(df['hhinc'] <= 60000) & (df['auto_suff'] == 0), 'market_seg'] = 0
        df.loc[(df['hhinc'] > 60000) & (df['auto_suff'] == 0), 'market_seg'] = 1
        df.loc[(df['hhinc'] <= 60000) & (df['auto_suff'] == 1), 'market_seg'] = 2
        df.loc[(df['hhinc'] > 60000) & (df['auto_suff'] == 1), 'market_seg'] = 3
        df.loc[(df['hhinc'] <= 60000) & (df['auto_suff'] == 2), 'market_seg'] = 4
        df.loc[(df['hhinc'] > 60000) & (df['auto_suff'] == 2), 'market_seg'] = 5
        # set dtype
        df['market_seg'] = df['market_seg'].astype('int8')
    else:
        raise KeyError ("The requisite fields are not there to run the function")

    return df

# Method to bring in the various dtype definitions
def set_dtype_defintions(filepath, filenames):

    """
    This function batches in the dtype definition JSON file for each of the file in the filelist.

    :param filepath: directory in which the user has saved all the requisite files noted in control_parameters.py
    :param filenames: JSON filename that needs to be evaluated
    :return: variable names of each dtype file
    """

    # Batch in the dtype definitions that are stored as json files
    dataFrameDtype = {}

    for filename in filenames:
        with open(os.path.join(filepath, filename)) as json_file:
            dataFrameDtype[filename] = json.load(json_file, object_pairs_hook=OrderedDict)

    return  dataFrameDtype


    # Function to check existence of files
def file_existence(filepath, filename):

    """
    This function checks if a file exists for a given user directory
    :rtype: object
    :param: filepath: directory in which the user has saved all the requisite files noted in control_parameters.py
    :param: filename: filename that needs to be checked for its presence
    :return: boolean
    """
    try:
        f = open(os.path.join(filepath, filename))

    except IOError as e:
        print("%s: %s : %s" % (filepath, filename, e.strerror))
        return False

    return True

def convert_df(ggh, dirlisting, filename, nzones):
    """
    This function reads in a trip matrix in the binary format and transforms it for use in sampling a destination
    for an origin.
    :param ggh:
    :param filename:
    :param nzones:
    :return:
    """

    # read in the fortran dataframe and then subset it for the internal zones
    # in the GGH.
    df = read_fortran_rectangle(os.path.join(dirlisting, filename), n_columns=4000,
                                tall=False, reindex_rows=False, fill_value=None)
    df1 = pd.DataFrame(df).iloc[:nzones, :nzones]

    # set column and row indices
    df1.rename(columns=ggh['ggh_zone'], inplace=True)
    df1.set_index(ggh['ggh_zone'], inplace=True)

    # Now unstack and rename columns
    df1 = df1.unstack().reset_index()
    df1.columns = ['origin', 'destination', 'trips']

    # dictionary of market segment key and values
    market_seg_def = {
        'nocar_low.bin': 0,
        "nocar_high.bin": 1,
        "insuff_low.bin": 2,
        "insuff_high.bin": 3,
        "suff_low.bin": 4,
        "suff_high.bin": 5,
        "all_segments.bin": 10
    }

    # Remove zero trips and add in market segmentation and peak-offpeak flag
    df1 = df1.loc[df1['trips'] != 0]
    segment = filename.split('_')
    s1 = segment[5] + '_' + segment[6]
    df1['market_seg'] = s1
    df1['mseg'] = df1['market_seg'].map(market_seg_def)
    df1['period'] = segment[1]
    df1.drop('market_seg', axis=1, inplace=True)

    # Also add in the rounded up trips values. This is important as these integer trips act as sampling weights
    # when choosing a destination for a given O-D pair
    # df1['wholetrips'] = round(df1['trips']).astype(int)
    df1['wholetrips'] = df1['trips']
    df1 = df1.loc[df1['wholetrips'] > 0.01]

    return df1


def batchin_binaryfiles():

    # set empty dictionary
    all_other = {}


    global new_taz_j
    # batch in ggh zone numbers and add in two columns for i and j zones
    ggh = pd.read_csv(os.path.join(control_parameters.inputDirListing, ev.EarlyValidFiles.GGH_EQUIV))
    ggh['key'] = 0
    # make a copy of the df and create a square matrix
    ggh1 = ggh
    ggh2 = pd.merge(ggh1, ggh, how='left', on='key')

    # batch in the binary files into a dictionary
    for filename in ev.EarlyValidFiles.getBINFileList():

        all_other[filename] = convert_df(ggh, control_parameters.dirListing_othertrips, filename, 3262)
        control_parameters.logger.info("Batched in non-mandatory file %s" % filename)

        # reset column types
        for key, value in ev.EarlyValidFiles.dict_nonmandatory_dtype.items():
            all_other[filename][key] = all_other[filename][key].astype(value)

    return (all_other, ggh2)
