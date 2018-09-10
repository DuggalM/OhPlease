# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 18:07:02 2017

@author: MZD
"""
import numpy as np
import common

# This file contains all the user defined controls like directory listing, filelists, binary lists etc.
# All modifications to customize a run should be made here.
########################################################################################################################
# user to set file path and set file names if different from the default
inputDirListing             = 'c:\\personal\\IMM\\Inputs\\'
outputDirListing            = 'c:\\personal\\IMM\\Outputs\\'
dirListing_othertrips       = 'c:\\personal\\IMM\\Inputs\\Other Trips\\'
dirListing_mlogit_prob      = 'c:\\personal\IMM\\MLOGIT\\outputs\\'
dirListing_mlogitmatrices   = 'C:\\personal\\IMM\\MLOGIT\\emmebin\\'
dirListing_mlogit_controls  = 'c:\\personal\IMM\\MLOGIT\\MLOGIT'

# set random seed to be used
seed = 12345
prng = np.random.RandomState(seed)
chaos_monkey = 0.01
logger = common.setupLogger("MLOGIT PROBE", "mandatory_nonmandatory.log")

# set chunk parameter. This should be the same as in MLogit for outputting probabilities and equals the number of
# files for each trip purpose and time period in the binary probability list
chunk = 1


########################################################################################################################
# BINARY PROBABILITIES
# Bill's binary probability and access/egress station ids split into chunks. There must be:
# 7 (trip purposes) X 3 (elemental probabilities, station choice, egress mode probabilities) X 2 (time periods) X
# 1 (chunks) = 42 files.

# TODO-mausam add in the remaining trip purposes as well

binary_dict = {
    'hbw': [('hbw_mode_peak_bin', ['hbw_peak_tresodat_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbw_mode_offpeak_bin', ['hbw_offpeak_tresodat_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbw_stn_peak_bin', ['hbw_peak_tresosta_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbw_stn_offpeak_bin', ['hbw_offpeak_tresosta_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbw_egg_peak_bin', ['hbw_peak_tresoegr_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbw_egg_offpeak_bin', ['hbw_offpeak_tresoegr_%s.bin' % str(i) for i in range(1, chunk + 1)])],

    'hbs': [('hbs_mode_peak_bin', ['hbs_peak_tresodat_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbs_mode_offpeak_bin', ['hbs_offpeak_tresodat_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbs_stn_peak_bin', ['hbs_peak_tresosta_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbs_stn_offpeak_bin', ['hbs_offpeak_tresosta_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbs_egg_peak_bin', ['hbs_peak_tresoegr_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbs_egg_offpeak_bin', ['hbs_offpeak_tresoegr_%s.bin' % str(i) for i in range(1, chunk + 1)])],

    'hbu': [('hbu_mode_peak_bin', ['hbu_peak_tresodat_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbu_mode_offpeak_bin', ['hbu_offpeak_tresodat_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbu_stn_peak_bin', ['hbu_peak_tresosta_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbu_stn_offpeak_bin', ['hbu_offpeak_tresosta_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbu_egg_peak_bin', ['hbu_peak_tresoegr_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbu_egg_offpeak_bin', ['hbu_offpeak_tresoegr_%s.bin' % str(i) for i in range(1, chunk + 1)])],

    'hbm': [('hbm_mode_peak_bin', ['hbm_peak_tresodat_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbm_mode_offpeak_bin', ['hbm_offpeak_tresodat_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbm_stn_peak_bin', ['hbm_peak_tresosta_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbm_stn_offpeak_bin', ['hbm_offpeak_tresosta_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbm_egg_peak_bin', ['hbm_peak_tresoegr_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbm_egg_offpeak_bin', ['hbm_offpeak_tresoegr_%s.bin' % str(i) for i in range(1, chunk + 1)])],

    'hbo': [('hbo_mode_peak_bin', ['hbo_peak_tresodat_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbo_mode_offpeak_bin', ['hbo_offpeak_tresodat_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbo_stn_peak_bin', ['hbo_peak_tresosta_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbo_stn_offpeak_bin', ['hbo_offpeak_tresosta_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbo_egg_peak_bin', ['hbo_peak_tresoegr_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('hbo_egg_offpeak_bin', ['hbo_offpeak_tresoegr_%s.bin' % str(i) for i in range(1, chunk + 1)])],

    'nhb': [('nhb_mode_peak_bin', ['nhb_peak_tresodat_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('nhb_mode_offpeak_bin', ['nhb_offpeak_tresodat_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('nhb_stn_peak_bin', ['nhb_peak_tresosta_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('nhb_stn_offpeak_bin', ['nhb_offpeak_tresosta_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('nhb_egg_peak_bin', ['nhb_peak_tresoegr_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('nhb_egg_offpeak_bin', ['nhb_offpeak_tresoegr_%s.bin' % str(i) for i in range(1, chunk + 1)])],

    'wbo': [('wbo_mode_peak_bin', ['wbo_peak_tresodat_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('wbo_mode_offpeak_bin', ['wbo_offpeak_tresodat_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('wbo_stn_peak_bin', ['wbo_peak_tresosta_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('wbo_stn_offpeak_bin', ['wbo_offpeak_tresosta_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('wbo_egg_peak_bin', ['wbo_peak_tresoegr_%s.bin' % str(i) for i in range(1, chunk + 1)]),
            ('wbo_egg_offpeak_bin', ['wbo_offpeak_tresoegr_%s.bin' % str(i) for i in range(1, chunk + 1)])],


    
}
