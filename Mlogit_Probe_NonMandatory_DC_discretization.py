# -*- coding: utf-8 -*-
"""
Created on Thu Dec  10 18:07:02 2017

@author: MZD
"""

# import packages
import os
import pandas as pd
pd.options.mode.chained_assignment = 'raise'
import numpy as np
from balsa.matrices import to_fortran, read_fortran_rectangle
import EarlyValid as ev
import common
import control_parameters


class NonMandatoryFortranOd(object):
    
    """
    
    """
    
    def __init__(self):

        pass


    def convert_df(self, ggh, dirlisting, filename, nzones):
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

    def sample_destination(self, current_row, all_othertrips, chaos_monkey, prng):
        """
        This function samples a destination for a given origin based on the trip purpose and market segment chosen.

        :param current_row: row that has the origin for which a destination needs to be sampled
        :param all_othertrips: dictionary of names for the other trip matrices
        :return: single value representing the destination sampled
        """

        # create the key using the purpose and market segment. Then get the dataframe that belongs to the key
        # Now subset the dataframe by origin being evaluated. This is required for accurately sampling
        t1 = all_othertrips[ev.EarlyValidFiles.dict_othertrips_names.get(current_row[22])]
        zone_loc = current_row[7]  # save current_row origin taz
        t1_loc = t1.iloc[np.where(t1['origin'].values == zone_loc)]

        # if the t1_loc df is empty it means that the Dest Choice model did not produce a trip from that origin
        # for the origin, time period, and market segment in question. One needs to pick another zone
        counter = 1
        ZONE_RANGE = [1001, 9331]

        newzone_loc = zone_loc + counter
        while len(t1_loc) == 0:
            if (newzone_loc > ZONE_RANGE[1]):
                counter = -1
                newzone_loc = zone_loc + counter
            t1_loc = t1.iloc[np.where(t1['origin'].values == newzone_loc)]
            newzone_loc = newzone_loc + counter

        # generate a random number for exploring the destination space. In essence, given that discretization does not
        # have any fractions and we have rounded the trips before sampling, there is a reasonably high probability
        # that while sampling for destinations we routinely sample one specific zone. By setting an exploration threshold
        # we allow for a non-zero probability that every once a while the sampling space will be set equal across all
        # destination zones. This will avoid a clustering of trips to a destination.
        exploration_coeff = np.random.uniform(0,1,1)

        if exploration_coeff > chaos_monkey:

            # sample for a destination
            sampled_dest = t1_loc.sample(n= 1, weights= t1['trips'], replace=True, random_state= prng)
            # mprobe_valid.logger.info("Destination %s sampled using trips as a weight" %sampled_dest)

            return sampled_dest.iat[0, 1]

        else:

            # sample for a destination
            sampled_dest = t1_loc.sample(n= 1, replace=True, random_state= prng)
            # mprobe_valid.logger.info("Destination %s sampled with equal probability" %sampled_dest)

            return sampled_dest.iat[0, 1]


    def destination_solver(self, trips_hhold_array, chaos_monkey):
        """

        :param all_other:
        :param trips_hhold:
        :return:
        """
        # set empty dictionary
        all_other = {}

        prng = control_parameters.prng

        global new_taz_j
        # batch in ggh zone numbers and add in two columns for i and j zones
        ggh = pd.read_csv(os.path.join(control_parameters.inputDirListing, ev.EarlyValidFiles.GGH_EQUIV))
        ggh['key'] = 0
        # make a copy of the df and create a square matrix
        ggh1 = ggh
        self.ggh2 = pd.merge(ggh1, ggh, how='left', on='key')

        # batch in the binary files into a dictionary
        for filename in ev.EarlyValidFiles.getBINFileList():

            all_other[filename] = self.convert_df(ggh, control_parameters.dirListing_othertrips, filename, 3262)
            control_parameters.logger.info("Batched in non-mandatory file %s" % filename)

            # reset column types
            for key, value in ev.EarlyValidFiles.dict_nonmandatory_dtype.items():
                all_other[filename][key] = all_other[filename][key].astype(value)


        nrows, ncols = trips_hhold_array.shape

        LOG_EVERY_N = 10000

        for row in range(nrows):
            if (row % LOG_EVERY_N) == 0:
                control_parameters.logger.info("Solving household number %s and person %s" % (trips_hhold_array[row][0], trips_hhold_array[row][1]))

            nrows, ncols = trips_hhold_array.shape

            # this first condition is the start of the loop
            if (trips_hhold_array[row][7] > 0) & (trips_hhold_array[row][8] == 0):
                # get the zone by sampling from the requisite trip purpose, time period and market segment
                # and assign as the destination
                new_taz_j = self.sample_destination(trips_hhold_array[row], all_other, chaos_monkey, prng)
                trips_hhold_array[row][8] = new_taz_j

            # this is the next condition the destination is known but not the origin
            # the destination from the previous row becomes the origin
            if (trips_hhold_array[row][7] == 0) & (trips_hhold_array[row][8] != 0):
                trips_hhold_array[row][7] = new_taz_j

            # final condition where neither origin or destination is defined
            # in this case the destination from the previous row becomes the origin
            # and a destination is sampled from the requisite trip purpose, time period and market segment
            if (trips_hhold_array[row][7] == 0) & (trips_hhold_array[row][8] == 0):
                trips_hhold_array[row][7] = new_taz_j
                test_current = trips_hhold_array[row]

                new_taz_j = self.sample_destination(test_current, all_other,chaos_monkey, prng)
                trips_hhold_array[row][8] = new_taz_j

        return trips_hhold_array


    def run(self, trips_hhold, nonmandatory_purposes, chaos_monkey):

        # run destination solver. But first translate the trips_hhold dataframe to a numpy array. This results in a
        # drop in run times. Unlike the peak solver which saw a drop from 30 mins to 20 seconds, the destination
        # solver sees around a 50% run time savings to around 2 hours.

        # some housekeeping before running the destination solver function. First, create the flag that will help
        # choose the appropriate non-mandatory matrix to sample from.

        control_parameters.logger.info("Prepare the trips_hhold dataframe for the destination solver function")
        nrows_trips_hhold = trips_hhold.shape[0]
        trips_hhold['dict_flag'] = trips_hhold['purpose'].astype(str) + '_' + trips_hhold['market_seg'].apply(str) + '_' + \
                              trips_hhold['peak_flag'].apply(str)


        # Second, there are many instances where the person only makes mandatory tours, in which case we don't need to
        # evaluate it. Thus, only keep records where the taz_j has a 0 to run the destination solver. Create a flag to
        # help identify the appropriate records
        control_parameters.logger.info("Getting households and person trip records that have more than just manadatory trips,"
                                 "thereby needing the destination solver.")
        tgr = trips_hhold.iloc[np.where(trips_hhold['taz_j'].values == 0)].\
            groupby(['hhid', 'pid']).\
            size().\
            reset_index(name="count")
        tgr['solver_flag'] = 1
        tgr.drop('count', axis=1, inplace = True)

        # transfer the flag information to the trips_hhold while holding it in a temp_df and slicing it to hold the
        # requisite records.
        trips_hhold = pd.merge(trips_hhold, tgr, how='left', on=['hhid', 'pid'])
        trips_hhold['solver_flag'].fillna(0, inplace=True)
        # create temp df to run through the destination solver
        temp_df = trips_hhold
        temp_df = temp_df.iloc[np.where(temp_df['solver_flag'].values == 1)]
        control_parameters.logger.info(
            "A total of %s nonmandatory trips will be assigned a origin and/or destination" % temp_df.shape[0])

        control_parameters.logger.info("Running the destination solver. Please be patient. There are too many records and machinations"
                                 "that need to be completed before it all ends.")
        trips_hhold_array = temp_df.values
        trips_hhold_array = self.destination_solver(trips_hhold_array, chaos_monkey)
        trips_hhold_dest_df = pd.DataFrame(trips_hhold_array)
        trips_hhold_dest_df.columns = trips_hhold.columns

        # The records are now concatenated back to the original trips_hhold df, but as a replacement
        control_parameters.logger.info("Concatenating the records back")
        trips_hhold = trips_hhold.iloc[np.where(trips_hhold['solver_flag'].values == 0)]
        trips_hhold = common.concat_df(trips_hhold, trips_hhold_dest_df, 0)
        trips_hhold.sort_values(['hhid', 'pid'], inplace= True, ascending = True)

        trips_hhold = trips_hhold.astype(dtype={

            "hhid": "int32",
            "pid": "int8",
            "tour_id": "int8",
            "subtour_id": "int8",
            "trip_id": "int8",
            "activity_i": "category",
            "activity_j": "category",
            "taz_i": "int16",
            "taz_j": "int16",
            "tour_direction": "category",
            "purpose": "category",
            "trip_direction": "category",
            "peak_factor": "float64",
            "taz": "int16",
            "hhinc": "int32",
            "dtype": "int8",
            "hhsize": "int8",
            "nveh": "int8",
            "auto_suff": "int8",
            "market_seg": "int8",
            "rnum": "float64",
            "peak_flag": "int8",
            "dict_flag": "category",
            "solver_flag": "float64"
        })


        # now batch out the necessary matrices
        control_parameters.logger.info("Start saving the matrices in the format desired by Mlogit")
        for purpose in nonmandatory_purposes:

            nonmand_only = trips_hhold[trips_hhold['purpose'].values == purpose].copy()
            # set the market segment to 0 as NHB has no market segment and Bill's prob file will have this as 1. We
            # will reset 1 to 0 during mode choice discretization
            if purpose == "NHB":
                nonmand_only['market_seg'] = 0

            # now loop over the peak periods
            for peak in range(0, 2):

                timeperiod_df = nonmand_only[nonmand_only['peak_flag'] == peak].copy()
                timeperiod_df = timeperiod_df.groupby(['taz_i', 'taz_j', 'purpose', 'market_seg']).size().\
                    reset_index(name='freq')

                # now loop over the segments
                for segment in timeperiod_df['market_seg'].unique():
                    # create filename and then groupby
                    # only keep relevant cols and set a flag
                    # Merge the ggh zones and the trip list and convert to wide format

                    dataFrameDtype = common.set_dtype_defintions(control_parameters.inputDirListing,
                                                                 ev.EarlyValidFiles.getJSONFileList())
                    mtx_name = dataFrameDtype[ev.EarlyValidFiles.MATRIX_NAMES]

                    # the matrices have to be given a specific filename that corresponds to the control file for MLOGIT
                    fname = purpose + "_" + str(segment) + "_" + str(peak)
                    for key, value in mtx_name.items():
                        if fname == key:
                            fname_mtx = value
                            control_parameters.logger.info("The %s matrix is being saved" % fname_mtx)

                    df_hbw = timeperiod_df[timeperiod_df['market_seg'] == segment].copy()
                    df_hbw = df_hbw[['taz_i', 'taz_j']]
                    df_hbw['probflag'] = 1

                    # Make square dataframe for Fortran
                    df_hbw1 = pd.merge(self.ggh2, df_hbw, how="left", left_on=['ggh_zone_x', 'ggh_zone_y'],
                                       right_on=['taz_i', 'taz_j'])
                    df_hbw2 = df_hbw1.pivot_table(index='ggh_zone_x', columns='ggh_zone_y', values='probflag',
                                                  fill_value=0)

                    to_fortran(df_hbw2,
                               os.path.join(control_parameters.dirListing_mlogitmatrices, fname_mtx + '.bin'),
                               n_columns = 4000)

        return trips_hhold








