# -*- coding: utf-8 -*-
"""
Created on Thu Dec  10 18:07:02 2017

@author: MZD
"""

# import packages
import os
import pandas as pd
pd.options.mode.chained_assignment = 'raise'
import EarlyValid as ev
import common
import control_parameters

class TripsHhold(object):


    def __init__(self):

        # batch requisite json file for DTYPE
        control_parameters.logger.info("Get DTYPE definitions for the various files")
        self.dataFrameDtype = common.set_dtype_defintions(control_parameters.inputDirListing,
                                                          ev.EarlyValidFiles.getJSONFileList())

    def run(self, trips, hh):

        # set dtypes for the household and trips dataframe to reduce memory requirements
        for key, value in self.dataFrameDtype[ev.EarlyValidFiles.DTYPE_TRIPS].items():
            trips[key] = trips[key].astype(value)

        for key, value in self.dataFrameDtype[ev.EarlyValidFiles.DTYPE_HOUSEHOLDS].items():
            hh[key] = hh[key].astype(value)

        # Merge the hholds info to the trips. By doing so, we can bring in a bunch of household attributes
        # including income, dwelling type, size, number of vehicles, and auto_sufficiency. Add in an integer
        # definition for one of six market segments.
        trips_hhold = pd.merge(trips, hh, how='left', left_on='hhid', right_on='hhid')

        return (hh, trips, trips_hhold)
