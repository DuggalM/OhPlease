# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 18:07:02 2017

@author: MZD
"""



import pandas as pd
pd.options.mode.chained_assignment = 'raise'
import numpy as np
import os
import os.path
import control_parameters
from balsa.cheval import sample_from_weights
import EarlyValid as ev
import common


class VehicleSampling(object):
    """
    This class is used to assign a vehicle (trad auto, av auto, trad uber, auto uber) to each household in the GGHM.

    The sequence of the code is defined as follows:

    step 0: early validation - this ensures that all the files needed for vehicle sampling are available in the user
            defined directory listing. These files are noted by the user in the early_valid_filelist.
    step 1: binary file validation - here we make sure that the number of binary files in the directory match the
            number of chunks noted in the control_parameters file. This is important as it ensures that MLOGIT
            sliced the probability dataframe into the requisite number of chunks.
    step 2: function that assigns a vehicle type to each household.
    step 3: the run function that takes in the data that the model operates on carries out vehicle sampling.


    """


    def __init__(self):

        pass


    def assign_vehtype_hhold(self, hh, veh_type, prng):

        """
        This function takes the household file and processed vehicle type file and samples a vehicle to attach to each
        household.
        :param hh_file: households file noted in the control_parameters file
        :param vehtype_file: vehicle type probability file noted in the control_parameters file
        :return: sample_df: A dataframe with the sampled vehicle type
        """

        # join the vehicle probabilities to the households so that we can sample from them. It is easy enough
        # to attach the probabilities because we know the market segment of each household.

        hh_vehprob = pd.merge(hh, veh_type, left_on=['taz', 'market_seg'],
                              right_on=['taz', 'market_seg'], how='left')

        # now unstack and get it ready for Cheval
        hh_vehprob['vtype'] = hh_vehprob['vtype'].astype('category')
        hh_vehprob = hh_vehprob.pivot(index='hhid', columns='vtype', values='value')

        # Sample a vehicle type using Cheval
        sample_df = pd.DataFrame(sample_from_weights(hh_vehprob, randomizer=prng, astype='category', n_threads=3))
        sample_df.columns = ['hh_veh_type']

        hh_file = common.concat_df(hh, sample_df, 1)


        return hh_file

    def run(self, hh, trips, veh_type, prng):
        """
        This function runs the vehicle sampling for the households


        :return:
        """


        veh_type.rename(columns={'ggh_zone': 'taz'}, inplace=True)
        veh_type = pd.melt(veh_type, id_vars=['taz']).sort_values(['taz', 'variable'])

        # attach the market segment to the veh_type. Also add in an integer based market seg.
        # The vehicle type is part of the variable column but starts after the second underscore
        # thus it is stripped out into a column of its own.
        veh_type['mseg1'] = veh_type['variable'].str.split('_').str[0]
        veh_type['mseg2'] = veh_type['variable'].str.split('_').str[1]
        veh_type['mseg'] = veh_type['mseg1'] + '_' + veh_type['mseg2']

        # add in integer based market segment category
        veh_type.loc[(veh_type['mseg'] == 'nocar_low'), 'market_seg'] = 0
        veh_type.loc[(veh_type['mseg'] == 'nocar_high'), 'market_seg'] = 1
        veh_type.loc[(veh_type['mseg'] == 'insuff_low'), 'market_seg'] = 2
        veh_type.loc[(veh_type['mseg'] == 'insuff_high'), 'market_seg'] = 3
        veh_type.loc[(veh_type['mseg'] == 'suff_low'), 'market_seg'] = 4
        veh_type.loc[(veh_type['mseg'] == 'suff_high'), 'market_seg'] = 5
        veh_type['market_seg'] = veh_type['market_seg'].astype('int8')

        # extract the vehicle type and drop unncessary columns
        veh_type['vtype1'] = veh_type['variable'].str.split('_').str[2]
        veh_type['vtype2'] = veh_type['variable'].str.split('_').str[3]
        veh_type['vtype'] = veh_type['vtype1'] + '_' + veh_type['vtype2']
        columns = ['mseg1', 'mseg2', 'mseg', 'vtype1', 'vtype2']
        veh_type.drop(columns, inplace=True, axis=1)

        ################################################################################################################
        # RUN VEHICLE SAMPLING

        # invoke the class and run the vehicle sampling method.
        control_parameters.logger.info("Add vehicle type to every household")
        hh = self.assign_vehtype_hhold(hh, veh_type, prng)

        # only keep the hhid and veh_type column
        hh = hh[['hhid', 'hh_veh_type']]

        # dictionary of market and vehicle segment key and values
        market_seg_def = {
            0: 'nocar_low',
            1: "nocar_high",
            2: "insuff_low",
            3: "insuff_high",
            4: "suff_low",
            5: "suff_high"
        }

        # dictionary of veh segment key and values
        veh_seg_def = {
            'trad_auto': 0,
            "trad_uber": 1,
            "av_auto": 2,
            "av_uber": 3
        }

        # transfer the veh_type and market_segment by household id to the trips table.
        # Add in a descriptor for the market segment to make it easy to understand
        trips = pd.merge(trips, hh, on='hhid', how='left')

        # map the information and add flag
        trips['mseg'] = trips['market_seg'].map(market_seg_def)
        trips['vseg'] = trips['hh_veh_type'].map(veh_seg_def)
        trips['market_temp'] = np.where(trips['purpose'].isin(['HBS', 'HBU']), 0, trips['market_seg'])
        # trips['flag'] = np.where(trips['purpose'].isin(['HBS', 'HBU']),
        #                          trips['taz_i'].astype(str) + trips['taz_j'].astype(str) + str(0),
        #                          trips['taz_i'].astype(str) + trips['taz_j'].astype(str) + trips['market_seg'].astype(
        #                              str))
        control_parameters.logger.info("create veh flag")
        trips['flag'] = trips['taz_i'].astype(str) + trips['taz_j'].astype(str) + trips['market_temp'].astype(str)
        trips.drop('market_temp', axis=1, inplace=True)

        control_parameters.logger.info("Vehicle type information transferred to every trip record via household. This dataframe is"
                           "now ready for mode sampling.")
        return trips



