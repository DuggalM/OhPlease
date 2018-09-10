import pandas as pd
import validation
import starttimes
from multiprocessing import Pool, cpu_count
from functools import partial
import itertools
from numpy.random import RandomState
import cProfile
import functools
import os

cpu_cores = cpu_count()
# validation.logger.info("There are %s cpu cores available" %cpu_cores)
prng = RandomState(123)

def collect_results(result_list):
    return pd.DataFrame({'start_time': result_list[0::4],
                  'arrival_time': result_list[1::4],
                  'tour_id': result_list[2::4],
                  'trip_id': result_list[3::4]})


if __name__ == '__main__':

    ##################### SERIAL CODE ##################################################################################
    # Run the serial code
    st = starttimes.StartTimesCreate(prng)
    temp_df, two_trips_df, time_dist_arr = st.run()
    validation.logger.info("Serial code processing is over")

    # Prepare the dataframe to sample start times. Create groups from the input dataframe
    temp_df1 = st.prepare_two_trips_more_df(temp_df, two_trips_df)
    validation.logger.info("Dataframe prepared for multiprocessing")

    ##################### PARALLEL CODE ################################################################################

    validation.logger.info("Start creating groups to feed to multiprocessing.")
    grp_list = []
    for name, group in temp_df1.groupby('tour_id'):
        grp_list.append(group)
    validation.logger.info("Dataframe containing tours with more than 2 trips is prepared. There are a "
                           "total of %s tours to assess and %s trip records" %(len(grp_list), temp_df1.shape[0]))

    # set partial function to feed multiple arguments to Pool
    func_partial = partial(st.calculate_starttimes_morethan_twotrips, time_dist_arr=time_dist_arr)
    pool = Pool(cpu_cores)

    # Multiprocessing start
    with pool as p:
        # result_list = p.map(func_partial, grp_list)
        result_list = p.map(func_partial, grp_list)
    validation.logger.info("Multiprocessing completed")

    # make one list and then conver to dataframe
    merged = list(itertools.chain(*result_list))
    results_df = collect_results(merged)
    #
    # results_df.to_csv(r"c:/personal/imm/parallel_times.csv", index=False)

    pool.close()
    pool.join()
