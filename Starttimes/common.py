import pandas as pd
import os
from collections import OrderedDict
import json
import logging
import control_parameters

def setupLogger(model_name):
    # remove pre existing log
    # if os.path.exists(os.path.join(control_parameters.dirListing, control_parameters.logname)):
    #     os.remove(os.path.join(control_parameters.dirListing, control_parameters.logname))

    logger = logging.getLogger(model_name)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(os.path.join(control_parameters.dirListing, control_parameters.logname))
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s"))
    logger.addHandler(fh)

    return logger

# logger = setupLogger("Start_Times_Assignment")

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

def dtype_defintions(filepath, filenames):

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