# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 18:07:02 2017

@author: MZD
"""


import common
import control_parameters



# Early validation of files. 
# This includes checking for the ABM components as well as the necessary trips
# from the GGHM run.

class EarlyValidFiles(object):



    ####################### CSV ############################
    HOUSEHOLDS_OUT  = 'households_out.csv'
    TRIPS_OUT        = 'trips_out.csv'
    GGH_EQUIV        = 'GGH_zones.csv'
    SAMPLE_VEH_PROPS = 'sample_veh_proportions_gghm_zone_csd.csv'

    ####################### JSON ###########################
    DTYPE_HOUSEHOLDS = 'dtype_households.json'
    DTYPE_TRIPS      = 'dtype_trips.json'
    DTYPE_ELEMENTAL_PROB = 'dtype_primarymode_prob.json'
    DTYPE_STATION_CHOICE = 'dtype_stationchoice.json'
    DTYPE_EGRESS_PROB = 'dtype_egressmode_prob.json'
    DTYPE_TRIPS_PROCESSED = 'dtype_tripsprocessed.json'
    MATRIX_NAMES = 'matrix_names_mlogit.json'


    ####################### PEAK ############################
    HBM_PEAK_MSEG0 = 'trips_peak_all_modes_hbm_nocar_low.bin'
    HBM_PEAK_MSEG1 = 'trips_peak_all_modes_hbm_nocar_high.bin'
    HBM_PEAK_MSEG2 = 'trips_peak_all_modes_hbm_insuff_low.bin'
    HBM_PEAK_MSEG3 = 'trips_peak_all_modes_hbm_insuff_high.bin'
    HBM_PEAK_MSEG4 = 'trips_peak_all_modes_hbm_suff_low.bin'
    HBM_PEAK_MSEG5 = 'trips_peak_all_modes_hbm_suff_high.bin'
    
    HBO_PEAK_MSEG0 = 'trips_peak_all_modes_hbo_nocar_low.bin'
    HBO_PEAK_MSEG1 = 'trips_peak_all_modes_hbo_nocar_high.bin'
    HBO_PEAK_MSEG2 = 'trips_peak_all_modes_hbo_insuff_low.bin'
    HBO_PEAK_MSEG3 = 'trips_peak_all_modes_hbo_insuff_high.bin'
    HBO_PEAK_MSEG4 = 'trips_peak_all_modes_hbo_suff_low.bin'
    HBO_PEAK_MSEG5 = 'trips_peak_all_modes_hbo_suff_high.bin'
    
    WBO_PEAK_MSEG0 = 'trips_peak_all_modes_wbo_nocar_low.bin'
    WBO_PEAK_MSEG1 = 'trips_peak_all_modes_wbo_nocar_high.bin'
    WBO_PEAK_MSEG2 = 'trips_peak_all_modes_wbo_insuff_low.bin'
    WBO_PEAK_MSEG3 = 'trips_peak_all_modes_wbo_insuff_high.bin'
    WBO_PEAK_MSEG4 = 'trips_peak_all_modes_wbo_suff_low.bin'
    WBO_PEAK_MSEG5 = 'trips_peak_all_modes_wbo_suff_high.bin'

    HBE_PEAK_MSEG0 = 'trips_peak_all_modes_hbe_nocar_low.bin'
    HBE_PEAK_MSEG1 = 'trips_peak_all_modes_hbe_nocar_high.bin'
    HBE_PEAK_MSEG2 = 'trips_peak_all_modes_hbe_insuff_low.bin'
    HBE_PEAK_MSEG3 = 'trips_peak_all_modes_hbe_insuff_high.bin'
    HBE_PEAK_MSEG4 = 'trips_peak_all_modes_hbe_suff_low.bin'
    HBE_PEAK_MSEG5 = 'trips_peak_all_modes_hbe_suff_high.bin'
    
    NHB_PEAK       = 'trips_peak_all_modes_nhb_all_segments.bin'

    ###################### OFF-PEAK ##########################
    HBM_OFFPEAK_MSEG0 = 'trips_offpeak_all_modes_hbm_nocar_low.bin'
    HBM_OFFPEAK_MSEG1 = 'trips_offpeak_all_modes_hbm_nocar_high.bin'
    HBM_OFFPEAK_MSEG2 = 'trips_offpeak_all_modes_hbm_insuff_low.bin'
    HBM_OFFPEAK_MSEG3 = 'trips_offpeak_all_modes_hbm_insuff_high.bin'
    HBM_OFFPEAK_MSEG4 = 'trips_offpeak_all_modes_hbm_suff_low.bin'
    HBM_OFFPEAK_MSEG5 = 'trips_offpeak_all_modes_hbm_suff_high.bin'

    HBO_OFFPEAK_MSEG0 = 'trips_offpeak_all_modes_hbo_nocar_low.bin'
    HBO_OFFPEAK_MSEG1 = 'trips_offpeak_all_modes_hbo_nocar_high.bin'
    HBO_OFFPEAK_MSEG2 = 'trips_offpeak_all_modes_hbo_insuff_low.bin'
    HBO_OFFPEAK_MSEG3 = 'trips_offpeak_all_modes_hbo_insuff_high.bin'
    HBO_OFFPEAK_MSEG4 = 'trips_offpeak_all_modes_hbo_suff_low.bin'
    HBO_OFFPEAK_MSEG5 = 'trips_offpeak_all_modes_hbo_suff_high.bin'

    WBO_OFFPEAK_MSEG0 = 'trips_offpeak_all_modes_wbo_nocar_low.bin'
    WBO_OFFPEAK_MSEG1 = 'trips_offpeak_all_modes_wbo_nocar_high.bin'
    WBO_OFFPEAK_MSEG2 = 'trips_offpeak_all_modes_wbo_insuff_low.bin'
    WBO_OFFPEAK_MSEG3 = 'trips_offpeak_all_modes_wbo_insuff_high.bin'
    WBO_OFFPEAK_MSEG4 = 'trips_offpeak_all_modes_wbo_suff_low.bin'
    WBO_OFFPEAK_MSEG5 = 'trips_offpeak_all_modes_wbo_suff_high.bin'

    HBE_OFFPEAK_MSEG0 = 'trips_offpeak_all_modes_hbe_nocar_low.bin'
    HBE_OFFPEAK_MSEG1 = 'trips_offpeak_all_modes_hbe_nocar_high.bin'
    HBE_OFFPEAK_MSEG2 = 'trips_offpeak_all_modes_hbe_insuff_low.bin'
    HBE_OFFPEAK_MSEG3 = 'trips_offpeak_all_modes_hbe_insuff_high.bin'
    HBE_OFFPEAK_MSEG4 = 'trips_offpeak_all_modes_hbe_suff_low.bin'
    HBE_OFFPEAK_MSEG5 = 'trips_offpeak_all_modes_hbe_suff_high.bin'

    NHB_OFFPEAK = 'trips_offpeak_all_modes_nhb_all_segments.bin'

    #################################################################
    HBW_OFFPEAK_TRESO = 'hbw_offpeak_treso.ctl'
    HBU_OFFPEAK_TRESO = 'hbu_offpeak_treso.ctl'
    HBS_OFFPEAK_TRESO = 'hbs_offpeak_treso.ctl'
    HBO_OFFPEAK_TRESO = 'hbo_offpeak_treso.ctl'
    HBM_OFFPEAK_TRESO = 'hbm_offpeak_treso.ctl'
    WBO_OFFPEAK_TRESO = 'wbo_offpeak_treso.ctl'
    NHB_OFFPEAK_TRESO = 'nhb_offpeak_treso.ctl'

    HBW_PEAK_TRESO = 'hbw_peak_treso.ctl'
    HBU_PEAK_TRESO = 'hbu_peak_treso.ctl'
    HBS_PEAK_TRESO = 'hbs_peak_treso.ctl'
    HBO_PEAK_TRESO = 'hbo_peak_treso.ctl'
    HBM_PEAK_TRESO = 'hbm_peak_treso.ctl'
    WBO_PEAK_TRESO = 'wbo_peak_treso.ctl'
    NHB_PEAK_TRESO = 'nhb_peak_treso.ctl'

    

    @classmethod
    def getBINFileList(cls):
        return [
            cls.HBM_PEAK_MSEG0, cls.HBM_PEAK_MSEG1, cls.HBM_PEAK_MSEG2,
            cls.HBM_PEAK_MSEG3, cls.HBM_PEAK_MSEG4, cls.HBM_PEAK_MSEG5,
            cls.HBO_PEAK_MSEG0, cls.HBO_PEAK_MSEG1, cls.HBO_PEAK_MSEG2,
            cls.HBO_PEAK_MSEG3, cls.HBO_PEAK_MSEG4, cls.HBO_PEAK_MSEG5,
            cls.WBO_PEAK_MSEG0, cls.WBO_PEAK_MSEG1, cls.WBO_PEAK_MSEG2,
            cls.WBO_PEAK_MSEG3, cls.WBO_PEAK_MSEG4, cls.WBO_PEAK_MSEG5,
            cls.HBE_PEAK_MSEG0, cls.HBE_PEAK_MSEG1, cls.HBE_PEAK_MSEG2,
            cls.HBE_PEAK_MSEG3, cls.HBE_PEAK_MSEG4, cls.HBE_PEAK_MSEG5,
            cls.NHB_PEAK,
            cls.HBM_OFFPEAK_MSEG0, cls.HBM_OFFPEAK_MSEG1, cls.HBM_OFFPEAK_MSEG2,
            cls.HBM_OFFPEAK_MSEG3, cls.HBM_OFFPEAK_MSEG4, cls.HBM_OFFPEAK_MSEG5,
            cls.HBO_OFFPEAK_MSEG0, cls.HBO_OFFPEAK_MSEG1, cls.HBO_OFFPEAK_MSEG2,
            cls.HBO_OFFPEAK_MSEG3, cls.HBO_OFFPEAK_MSEG4, cls.HBO_OFFPEAK_MSEG5,
            cls.WBO_OFFPEAK_MSEG0, cls.WBO_OFFPEAK_MSEG1, cls.WBO_OFFPEAK_MSEG2,
            cls.WBO_OFFPEAK_MSEG3, cls.WBO_OFFPEAK_MSEG4, cls.WBO_OFFPEAK_MSEG5,
            cls.HBE_OFFPEAK_MSEG0, cls.HBE_OFFPEAK_MSEG1, cls.HBE_OFFPEAK_MSEG2,
            cls.HBE_OFFPEAK_MSEG3, cls.HBE_OFFPEAK_MSEG4, cls.HBE_OFFPEAK_MSEG5,
            cls.NHB_OFFPEAK
        ]

    @classmethod
    def getCSVFileList(cls):
        return [cls.HOUSEHOLDS_OUT, cls.TRIPS_OUT, cls.GGH_EQUIV, cls.SAMPLE_VEH_PROPS]
    
    @classmethod
    def getJSONFileList(cls):
        return [
            cls.DTYPE_EGRESS_PROB, cls.DTYPE_ELEMENTAL_PROB, cls.DTYPE_HOUSEHOLDS,
            cls.DTYPE_STATION_CHOICE, cls.DTYPE_TRIPS_PROCESSED, cls.DTYPE_TRIPS,
            cls.MATRIX_NAMES]

    @classmethod
    def getCTLFileList(cls):
        return [
            cls.HBW_PEAK_TRESO, cls.HBU_PEAK_TRESO, cls.HBS_PEAK_TRESO,
            cls.HBO_PEAK_TRESO, cls.HBM_PEAK_TRESO, cls.WBO_PEAK_TRESO,
            cls.NHB_PEAK_TRESO,
            cls.HBW_OFFPEAK_TRESO, cls.HBU_OFFPEAK_TRESO, cls.HBS_OFFPEAK_TRESO,
            cls.HBO_OFFPEAK_TRESO, cls.HBM_OFFPEAK_TRESO, cls.WBO_OFFPEAK_TRESO,
            cls.NHB_OFFPEAK_TRESO
        ]

    # dictionary of nonmandatory datafarmes by time period
    dict_othertrips_names = {
    # PEAK PERIOD
    'HBM_0_1': 'trips_peak_all_modes_hbm_nocar_low.bin',
    'HBM_1_1': 'trips_peak_all_modes_hbm_nocar_high.bin',
    'HBM_2_1': 'trips_peak_all_modes_hbm_insuff_low.bin',
    'HBM_3_1': 'trips_peak_all_modes_hbm_insuff_high.bin',
    'HBM_4_1': 'trips_peak_all_modes_hbm_suff_low.bin',
    'HBM_5_1': 'trips_peak_all_modes_hbm_suff_high.bin',
    'HBO_0_1': 'trips_peak_all_modes_hbo_nocar_low.bin',
    'HBO_1_1': 'trips_peak_all_modes_hbo_nocar_high.bin',
    'HBO_2_1': 'trips_peak_all_modes_hbo_insuff_low.bin',
    'HBO_3_1': 'trips_peak_all_modes_hbo_insuff_high.bin',
    'HBO_4_1': 'trips_peak_all_modes_hbo_suff_low.bin',
    'HBO_5_1': 'trips_peak_all_modes_hbo_suff_high.bin',
    'NHB_0_1': 'trips_peak_all_modes_nhb_all_segments.bin',
    'NHB_1_1': 'trips_peak_all_modes_nhb_all_segments.bin',
    'NHB_2_1': 'trips_peak_all_modes_nhb_all_segments.bin',
    'NHB_3_1': 'trips_peak_all_modes_nhb_all_segments.bin',
    'NHB_4_1': 'trips_peak_all_modes_nhb_all_segments.bin',
    'NHB_5_1': 'trips_peak_all_modes_nhb_all_segments.bin',
    'WBO_0_1': 'trips_peak_all_modes_wbo_nocar_low.bin',
    'WBO_1_1': 'trips_peak_all_modes_wbo_nocar_high.bin',
    'WBO_2_1': 'trips_peak_all_modes_wbo_insuff_low.bin',
    'WBO_3_1': 'trips_peak_all_modes_wbo_insuff_high.bin',
    'WBO_4_1': 'trips_peak_all_modes_wbo_suff_low.bin',
    'WBO_5_1': 'trips_peak_all_modes_wbo_suff_high.bin',
    'HBE_0_1': 'trips_peak_all_modes_hbe_nocar_low.bin',
    'HBE_1_1': 'trips_peak_all_modes_hbe_nocar_high.bin',
    'HBE_2_1': 'trips_peak_all_modes_hbe_insuff_low.bin',
    'HBE_3_1': 'trips_peak_all_modes_hbe_insuff_high.bin',
    'HBE_4_1': 'trips_peak_all_modes_hbe_suff_low.bin',
    'HBE_5_1': 'trips_peak_all_modes_hbe_suff_high.bin',

    # OFFPEAK PERIOD
    'HBM_0_0': 'trips_offpeak_all_modes_hbm_nocar_low.bin',
    'HBM_1_0': 'trips_offpeak_all_modes_hbm_nocar_high.bin',
    'HBM_2_0': 'trips_offpeak_all_modes_hbm_insuff_low.bin',
    'HBM_3_0': 'trips_offpeak_all_modes_hbm_insuff_high.bin',
    'HBM_4_0': 'trips_offpeak_all_modes_hbm_suff_low.bin',
    'HBM_5_0': 'trips_offpeak_all_modes_hbm_suff_high.bin',
    'HBO_0_0': 'trips_offpeak_all_modes_hbo_nocar_low.bin',
    'HBO_1_0': 'trips_offpeak_all_modes_hbo_nocar_high.bin',
    'HBO_2_0': 'trips_offpeak_all_modes_hbo_insuff_low.bin',
    'HBO_3_0': 'trips_offpeak_all_modes_hbo_insuff_high.bin',
    'HBO_4_0': 'trips_offpeak_all_modes_hbo_suff_low.bin',
    'HBO_5_0': 'trips_offpeak_all_modes_hbo_suff_high.bin',
    'NHB_0_0': 'trips_offpeak_all_modes_nhb_all_segments.bin',
    'NHB_1_0': 'trips_offpeak_all_modes_nhb_all_segments.bin',
    'NHB_2_0': 'trips_offpeak_all_modes_nhb_all_segments.bin',
    'NHB_3_0': 'trips_offpeak_all_modes_nhb_all_segments.bin',
    'NHB_4_0': 'trips_offpeak_all_modes_nhb_all_segments.bin',
    'NHB_5_0': 'trips_offpeak_all_modes_nhb_all_segments.bin',
    'WBO_0_0': 'trips_offpeak_all_modes_wbo_nocar_low.bin',
    'WBO_1_0': 'trips_offpeak_all_modes_wbo_nocar_high.bin',
    'WBO_2_0': 'trips_offpeak_all_modes_wbo_insuff_low.bin',
    'WBO_3_0': 'trips_offpeak_all_modes_wbo_insuff_high.bin',
    'WBO_4_0': 'trips_offpeak_all_modes_wbo_suff_low.bin',
    'WBO_5_0': 'trips_offpeak_all_modes_wbo_suff_high.bin',
    'HBE_0_0': 'trips_offpeak_all_modes_hbe_nocar_low.bin',
    'HBE_1_0': 'trips_offpeak_all_modes_hbe_nocar_high.bin',
    'HBE_2_0': 'trips_offpeak_all_modes_hbe_insuff_low.bin',
    'HBE_3_0': 'trips_offpeak_all_modes_hbe_insuff_high.bin',
    'HBE_4_0': 'trips_offpeak_all_modes_hbe_suff_low.bin',
    'HBE_5_0': 'trips_offpeak_all_modes_hbe_suff_high.bin'
    }

    # dictionary of Column DTYPES of the non-mandatory dataframe
    dict_nonmandatory_dtype = {
        'origin': 'int16',
        'destination': 'int16',
        'trips': 'float32',
        'mseg': 'int16',
        'wholetrips': 'int16',
        'period': 'category'
    }

    @classmethod
    def validation(cls):

        """
        This function validates if the files are available in the folder
        """
        _errorMessage = ""

        # Validation checks for files, both the JSON DTYPE and csv

        fileList = EarlyValidFiles.getJSONFileList()
        fileList.extend(EarlyValidFiles.getCSVFileList())
        fileList1 = EarlyValidFiles.getBINFileList()
        fileList2 = EarlyValidFiles.getCTLFileList()

        check_existence = True
        check_existence1 = True
        check_existence2 = True
        # Check if the trips_out, hholds_out, and JSON files noted in the filelist exist in the path specified
        # by the user. If not, then raise error.
        for file in fileList:


            check_existence = common.file_existence(control_parameters.inputDirListing, file)
            control_parameters.logger.info("%s necessary to run the program found in the directory" % file)

            if (not check_existence):
                control_parameters.logger.info("%s necessary to run the program NOT found in the directory" % file)
                return  False

        for file in fileList1:

            check_existence1 = common.file_existence(control_parameters.dirListing_othertrips, file)
            control_parameters.logger.info("%s necessary to run the program found in the directory" % file)

            if (not check_existence1):
                control_parameters.logger.info("%s necessary to run the program NOT found in the directory" % file)
                return  False

        for file in fileList2:

            check_existence2 = common.file_existence(control_parameters.dirListing_mlogit_controls, file)
            control_parameters.logger.info("%s necessary to run the program found in the directory" % file)

            if (not check_existence2):
                control_parameters.logger.info("%s necessary to run the program NOT found in the directory" % file)
                return False


            check_existence1 = common.file_existence(control_parameters.dirListing_othertrips, file)
            check_existence2 = common.file_existence(control_parameters.dirListing_mlogit_prob, file)
            control_parameters.logger.info("%s necessary to run the program found in the directory" % file)


        return True