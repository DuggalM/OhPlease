# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 18:07:02 2017

@author: MZD
"""

import control_parameters
import EarlyValid as ev
from trips_hhold_mixer import TripsHhold
from peak_offpeak import PeakOffpeak
from Mlogit_Probe_NonMandatory_DC_discretization_parallel import NonMandatoryFortranOd
from Mlogit_Probe_Mandatory import MandatoryFortranOd
import os
import pandas as pd
pd.options.mode.chained_assignment = 'raise'
import common
from vehicle_sampling import VehicleSampling
from mlogit_discretization import ModeSampling
from multiprocessing import Pool, cpu_count
from functools import partial
import launch_mlogit
import numpy as np



cpu_cores = cpu_count()-3

def main():

    ####################################################################################################################
    control_parameters.logger.info("Bring in the GLOBAL parameters")
    prng = control_parameters.prng
    chaos_monkey = control_parameters.chaos_monkey


    ####################################################################################################################
    control_parameters.logger.info("Undertake EARLY VALIDATION")
    # check if files exist
    valid = ev.EarlyValidFiles.validation()

    ####################################################################################################################
    control_parameters.logger.info("Batch in the household and trips file from a GGHM run and ATTACH MARKET SEGMENTS")
    hh = pd.read_csv(os.path.join(control_parameters.inputDirListing, ev.EarlyValidFiles.HOUSEHOLDS_OUT))
    trips = pd.read_csv(os.path.join(control_parameters.inputDirListing, ev.EarlyValidFiles.TRIPS_OUT))
    hh = common.market_segment(hh)  # tag each household by the market segment it belongs to

    ####################################################################################################################
    control_parameters.logger.info("Merge the household information to the trips file and also create the PEAK/OFF-PEAK"
                                   "flag.")
    hh, trips, trips_hhold = TripsHhold().run(trips, hh)
    trips_hhold = PeakOffpeak().run(trips_hhold, 1)

    ####################################################################################################################
    control_parameters.logger.info("Run MLOGIT PROBE FOR MANDATORY TRIP PURPOSE and save O-D pairs that MLOGIT "
                                   "needs to produce probabilities for.")
    mand_purposes = ['HBW', 'HBS', 'HBU']
    education = ['HBS', 'HBU']
    # mand_prob_pairs = MandatoryFortranOd().run(trips_hhold, mand_purposes, education)

    ####################################################################################################################
    control_parameters.logger.info("Run MLOGIT PROBE FOR NON-MANDATORY trip purposes. This will add an origin and/or "
                                   "destination to all non-mandatory trip records.")
    nonmandatory_purposes = ['HBO', 'HBM', 'WBO', 'NHB', 'HBE']
    trips_hhold = trips_hhold[(trips_hhold['hhid'] > 0) & (trips_hhold['hhid'] <= 100000)].copy()
    trips_hhold['parallel_flag'] = trips_hhold.groupby('hhid').ngroup()

    # batch in the Other trip purpose trip matrices and create slices of the trips_hhold dataframe given the number of
    # cores being used
    all_other, ggh2 = common.batchin_binaryfiles()
    grp_list = NonMandatoryFortranOd(all_other).slice_dataframe_forparallel(trips_hhold, cpu_cores)

    # Create partial function for Pool
    func_partial = partial(NonMandatoryFortranOd(all_other).run_dest_solver, chaos_monkey = chaos_monkey)

    control_parameters.logger.info("Start parallel processing")

    result_list = []
    pool = Pool(cpu_cores)
    with pool as p:

        result_list = p.map(func_partial,grp_list)
        control_parameters.logger.info("Multiprocessing completed")

    pool.close()
    pool.join()

    # One dataframe and reorder and set dtypes
    trips_hhold = pd.concat(result_list)
    trips_hhold = NonMandatoryFortranOd(all_other).reorder_setdtype(trips_hhold)

    # save the matrices for MLOGIT
    # NonMandatoryFortranOd(all_other).save_matrices(nonmandatory_purposes, trips_hhold, ggh2)
    ####################################################################################################################

    control_parameters.logger.info("Start running MLOGIT. This will take close to 20 hours so sit back and relax.")
    # launch_mlogit.LaunchingMlogit().runner_mlogit()

    ####################################################################################################################
    control_parameters.logger.info("Sample and attach VEHICLE TYPE to the households. This is needed for the mode "
                                   "probabilities are segmented by vehicle type.")
    veh_type = pd.read_csv(os.path.join(control_parameters.inputDirListing, ev.EarlyValidFiles.SAMPLE_VEH_PROPS))
    trips_hhold = VehicleSampling().run(hh, trips_hhold, veh_type, prng)

    ###################################################################################################################
    control_parameters.logger.info("Sample and attach MODES to the PEAK trip records")

    hbe = trips_hhold[trips_hhold['purpose'] == "HBE"].copy()
    trips_hhold = trips_hhold[trips_hhold['purpose'] != "HBE"].copy()
    print("A total of %s trips will be assigned a mode" %trips_hhold.shape[0])

    #####################################################
    # PEAK ONLY
    trips_vehtype_pk = trips_hhold[trips_hhold['peak_flag'] == 1].copy()

    hbw_pk = ModeSampling(prng).run("PEAK", "HBW", trips_vehtype_pk)
    control_parameters.logger.info("HBW peak trips discretized.")

    # Need to set the market segment of the school and univ trips to zero
    trips_vehtype_pk_edu = trips_vehtype_pk[
        (trips_vehtype_pk['purpose'] == 'HBS') | (trips_vehtype_pk['purpose'] == 'HBU')].copy()
    trips_vehtype_pk_edu['market_seg'] = 0
    hbs_pk = ModeSampling(prng).run("PEAK", "HBS", trips_vehtype_pk_edu)
    hbu_pk = ModeSampling(prng).run("PEAK", "HBU", trips_vehtype_pk_edu)
    control_parameters.logger.info("HBS and HBU peak trips discretized.")

    hbo_pk = ModeSampling(prng).run("PEAK", "HBO", trips_vehtype_pk)
    control_parameters.logger.info("HBO peak trips discretized.")

    hbm_pk = ModeSampling(prng).run("PEAK", "HBM", trips_vehtype_pk)
    control_parameters.logger.info("HBM peak trips discretized.")

    trips_vehtype_pk_nhb = trips_vehtype_pk[trips_vehtype_pk['purpose'] == 'NHB'].copy()
    trips_vehtype_pk_nhb['market_seg'] = 0
    nhb_pk = ModeSampling(prng).run("PEAK", "NHB", trips_vehtype_pk_nhb)
    control_parameters.logger.info("NHB peak trips discretized.")

    wbo_pk = ModeSampling(prng).run("PEAK", "WBO", trips_vehtype_pk)
    control_parameters.logger.info("WBO peak trips discretized.")

    all_peak_mc_discretized = pd.concat([hbw_pk, hbs_pk, hbu_pk,hbo_pk,hbm_pk, wbo_pk, nhb_pk], axis = 0)

    control_parameters.logger.info("Mode Choice discretized for the PEAK period")

    #####################################################
    # OFFPEAK ONLY
    trips_vehtype_offpk = trips_hhold[trips_hhold['peak_flag'] == 0].copy()

    hbw_offpk = ModeSampling(prng).run("OFF_PEAK", "HBW", trips_vehtype_offpk)
    control_parameters.logger.info("HBW off peak trips discretized.")

    # Need to set the market segment of the school and univ trips to zero
    trips_vehtype_offpk_edu = trips_vehtype_offpk[
        (trips_vehtype_offpk['purpose'] == 'HBS') | (trips_vehtype_offpk['purpose'] == 'HBU')].copy()
    trips_vehtype_offpk_edu['market_seg'] = 0
    hbs_offpk = ModeSampling(prng).run("OFF_PEAK", "HBS", trips_vehtype_offpk_edu)
    hbu_offpk = ModeSampling(prng).run("OFF_PEAK", "HBU", trips_vehtype_offpk_edu)
    control_parameters.logger.info("HBS and HBU off peak trips discretized.")

    hbo_offpk = ModeSampling(prng).run("OFF_PEAK", "HBO", trips_vehtype_offpk)
    control_parameters.logger.info("HBO off peak trips discretized.")

    hbm_offpk = ModeSampling(prng).run("OFF_PEAK", "HBM", trips_vehtype_offpk)
    control_parameters.logger.info("HBM off peak trips discretized.")

    trips_vehtype_offpk_nhb = trips_vehtype_offpk[trips_vehtype_offpk['purpose'] == 'NHB'].copy()
    trips_vehtype_offpk_nhb['market_seg'] = 0
    nhb_offpk = ModeSampling(prng).run("OFf_PEAK", "NHB", trips_vehtype_offpk_nhb)
    control_parameters.logger.info("NHB off peak trips discretized.")

    wbo_offpk = ModeSampling(prng).run("OFF_PEAK", "WBO", trips_vehtype_offpk)
    control_parameters.logger.info("WBO off peak trips discretized.")

    all_offpeak_mc_discretized = pd.concat([hbw_offpk, hbs_offpk, hbu_offpk, hbo_offpk, hbm_offpk, wbo_offpk, nhb_offpk], axis=0)

    control_parameters.logger.info("Mode Choice discretized for the OFF PEAK period")

    all_discretized = pd.concat([all_peak_mc_discretized, all_offpeak_mc_discretized], axis = 0)


    all_discretized.to_csv(r"c:\\personal\\imm\\outputs\\foo_all_Aug29.csv")


    control_parameters.logger.info("Processing Ended")
    print("")

if __name__ == "__main__":
    main()

