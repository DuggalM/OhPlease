# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 18:07:02 2017

@author: MZD
"""

# import packages
import os
import pandas as pd
pd.options.mode.chained_assignment = 'raise'
from balsa.matrices import to_fortran
import EarlyValid as ev
import common
import control_parameters


class MandatoryFortranOd(object):
    
    """
    
    """
    
    def __init__(self):

        pass



    def run(self, trips_hhold, mand_purposes, education):
        """

        :param mand_purposes: A list of mandatory trip purposes for which MLOGIT inputs need to be created
        :param education: the list of educational (school, university) trip purposes
        :return: saves Fortran ready binary files for Mlogit
        """

        # batch in ggh zone numbers and add in two columns for i and j zones
        ggh = pd.read_csv(os.path.join(control_parameters.inputDirListing, ev.EarlyValidFiles.GGH_EQUIV))
        ggh['key'] = 0
        # make a copy of the df and create a square matrix
        ggh1 = ggh
        ggh2 = pd.merge(ggh1, ggh, how='left', on='key')

        # generate the matrices desired by MLOGIT
        control_parameters.logger.info("Start evaluating the mandatory purposes")
        for purpose in mand_purposes:

            control_parameters.logger.info("Evaluating the %s purpose" % purpose)

            # because the school and university purposes don't have any market segmentation, set it to 0.
            if purpose in education:
                mand_only = trips_hhold[(trips_hhold['purpose'] == purpose)].copy()
                mand_only['market_seg'] = 0  # set this to a default market segment of 0
            else:
                mand_only = trips_hhold[(trips_hhold['purpose'] == purpose)].copy()

                # now loop over the peak periods
            for peak in range(0, 2):
                control_parameters.logger.info("Start evaluating the peak_flag %s" % peak)

                timeperiod_df = mand_only[mand_only['peak_flag'] == peak].copy()
                timeperiod_df = timeperiod_df.groupby(['taz_i', 'taz_j', 'purpose', 'market_seg']).size().reset_index(
                    name='freq')

                # now loop over the segments
                for segment in timeperiod_df['market_seg'].unique():
                    control_parameters.logger.info("Start evaluating the segment %s" % segment)
                    # only keep relevant cols and set a flag
                    # Merge the ggh zones and the trip list and convert to wide format

                    dataFrameDtype = common.set_dtype_defintions(control_parameters.inputDirListing,
                                                                 ev.EarlyValidFiles.getJSONFileList())
                    mtx_name = dataFrameDtype[ev.EarlyValidFiles.MATRIX_NAMES]

                    # the matrices have to be given a specific filename that coressponds to the control file for MLOGIT
                    fname = purpose + "_" + str(segment) + "_" + str(peak)
                    for key, value in mtx_name.items():
                        if fname == key:
                            fname_mtx = value
                            control_parameters.logger.info("The %s matrix is being saved" % fname_mtx)

                    df_hbw = timeperiod_df[timeperiod_df['market_seg'] == segment].copy()
                    df_hbw = df_hbw[['taz_i', 'taz_j']]
                    df_hbw['probflag'] = 1

                    # this merge is necessary to make a square matrix
                    df_hbw1 = pd.merge(ggh2, df_hbw, how="left", left_on=['ggh_zone_x', 'ggh_zone_y'],
                                       right_on=['taz_i', 'taz_j'])
                    df_hbw2 = df_hbw1.pivot_table(index='ggh_zone_x', columns='ggh_zone_y', values='probflag',
                                                  fill_value=0)

                    control_parameters.logger.info("Saving file to the requisite Fortran format")
                    to_fortran(df_hbw2,
                               os.path.join(control_parameters.dirListing_mlogitmatrices, fname_mtx + '.bin'),
                               n_columns = 4000)

        return trips_hhold



