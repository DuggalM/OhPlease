# -*- coding: utf-8 -*-
"""
Created on Thu Nov 30 18:07:02 2017

@author: MZD
"""

from vehicle_sampling import VehicleSampling
import control_parameters
from mlogit_discretization import ModeSampling
import common
import pandas as pd
pd.options.mode.chained_assignment = 'raise'
import os
import EarlyValid as ev
import numpy as np
import runner_MProbe
import builtins



def main():

    control_parameters.logger.info("Processing Start")
    # the sequence in which the various classes are called is the following:
    # step 0: set seed from the control parameters.py
    # step 1: call and run VehicleSampling class
    # step 2: run peak and then off-peak mode sampling for each trip purpose
    prng = control_parameters.prng

    ####################################################################################################################
    control_parameters.logger.info("Sample and attach vehicle type to the households")

    # TODO trips need to be set to the nonmand_pairs variable from runner_MProbe
    trips = pd.read_csv(r"C:\Personal\IMM\foo_nonmand_all.csv")

    # bring in the GGHMV4's household and trip list files and attach a market segment to each household
    control_parameters.logger.info("Batch in the household and trips list files from a gghm run")
    hh = pd.read_csv(os.path.join(control_parameters.inputDirListing, ev.EarlyValidFiles.HOUSEHOLDS_OUT))
    # trips = pd.read_csv(os.path.join(control_parameters.inputDirListing, ev.EarlyValidFiles.TRIPS_OUT))
    veh_type = pd.read_csv(os.path.join(control_parameters.inputDirListing, ev.EarlyValidFiles.SAMPLE_VEH_PROPS))

    # attach the market segment of each household
    hh = common.market_segment(hh)

    trips_vehtype = VehicleSampling().run(hh,trips,veh_type, prng)
    # trips_vehtype.iloc[0:500].to_csv(os.path.join(control_parameters.outputDirListing, 'foo_nonmand_veh.csv'), index = False)

    # ####################################################################################################################
    control_parameters.logger.info("Sample and attach elemental modes to the peak HBW trip records")

    # PEAK ONLY

    trips_vehtype_pk = trips_vehtype.loc[trips_vehtype['peak_flag'] == 1]

    hbw_pk = ModeSampling(prng).run("PEAK", "HBW", trips_vehtype_pk)
    control_parameters.logger.info("HBW peak trips discretized.")

    # Need to set the market segment of the school and univ trips to zero
    trips_vehtype_pk_edu = trips_vehtype_pk.loc[(trips_vehtype['purpose'] == 'HBS') | (trips_vehtype['purpose'] == 'HBU')]
    trips_vehtype_pk_edu['market_seg'] = 0
    hbs_pk = ModeSampling().run("PEAK", "HBS", trips_vehtype_pk_edu, prng).to_csv(r"c:/personal/imm/foo_hbspk_test.csv")
    hbu_pk = ModeSampling().run("PEAK", "HBU", trips_vehtype_pk_edu, prng).to_csv(r"c:/personal/imm/foo_hbupk_test.csv")
    control_parameters.logger.info("HBS and HBU peak trips discretized.")

    hbo_pk = ModeSampling().run("PEAK", "HBO", trips_vehtype_pk, prng).to_csv(r"c:/personal/imm/foo_hbopk_test.csv")
    control_parameters.logger.info("HBO peak trips discretized.")

    hbm_pk = ModeSampling().run("PEAK", "HBM", trips_vehtype_pk, prng).to_csv(r"c:/personal/imm/foo_hbmpk_test.csv")
    control_parameters.logger.info("HBM peak trips discretized.")

    trips_vehtype_pk_nhb = trips_vehtype_pk.loc[trips_vehtype['purpose'] == 'NHB']
    trips_vehtype_pk_nhb['market_seg'] = 0
    nhb_pk = ModeSampling().run("PEAK", "NHB", trips_vehtype_pk_nhb, prng).to_csv(r"c:/personal/imm/foo_nhbpk_test.csv")
    control_parameters.logger.info("NHB peak trips discretized.")

    wbo_pk = ModeSampling().run("PEAK", "WBO", trips_vehtype_pk, prng).to_csv(r"c:/personal/imm/foo_wbopk_test.csv")
    control_parameters.logger.info("WBO peak trips discretized.")



    # common.logger.info("Sample and attach elemental modes to the off-peak HBW trip records")
    # mand_sample_offpk = ModeSampling(seed).run("OFF_PEAK", "HBW", trips_vehtype)

    # final_df = pd.concat([hbw_pk, hbs_pk, hbu_pk, hbo_pk, hbm_pk, nhb_pk, wbo_pk], axis=0).\
    #     to_csv(r"c:/personal/imm/foo_mand_test.csv")
    # mand_sample_offpk.iloc[0:25000].to_csv(r"c:/personal/imm/foo.csv")

    ####################################################################################################################



    common.logger.info("Processing Ended")

    print("")
if __name__ == "__main__":
    main()
