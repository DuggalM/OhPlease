import pandas as pd
from multiprocessing import Pool, cpu_count
from functools import partial
import numpy as np
import itertools
import timeit
from numpy.random import RandomState
from numpy.random import choice


prng = RandomState(123)
cpu_cores = cpu_count()

def fun_array(group, time_dist_arr):
    """

    :param temp_array:
    :param time_dist_arr:
    :return:
    """
    results_frow = []

    temp_array = np.array(group.to_records())

    for i in range(0, len(temp_array)):
        if i == 0:

            start_time = temp_array[i]['start_time']
            arrival_time = temp_array[i]['arrival_time']
            tour_name = temp_array[i]['tour_id']
            trip_id = temp_array[i]['trip_id']
            results_frow.append(start_time)
            results_frow.append(arrival_time)
            results_frow.append(tour_name)
            results_frow.append(trip_id)
        else:

            tour_name = temp_array[i]['tour_id']  ### get the name of the tour being solved
            trip_id = temp_array[i]['trip_id']
            arrival_time_prev = results_frow[-3]  ### get the arrival time of the previous row as this serves as a constraint
            time_dist1_arr = time_dist_arr[
                time_dist_arr['Time'] >= arrival_time_prev]  ### slice the time distributions before sampling
            weight_column = temp_array[i]['weight_column']  ### get weight column to sample from

            #         #### sample a time and calculate a new arrival time as a result
            if time_dist1_arr.shape[0] > 0:

                probs = time_dist1_arr[weight_column]
                probs = probs / probs.sum()
                start_time = choice(time_dist1_arr['Time'], size=1, p=probs, replace=True)
                #             start_time = start_time[['Time']].values ###
                start_time = start_time[0]
            else:
                start_time = results_frow[-3]

            newarrival_time = start_time + temp_array[i][
                'ttime_mins'] / 60  ### caluclate the arrival time by adding start time to the travel time
            results_frow.append(start_time)
            results_frow.append(newarrival_time)
            results_frow.append(tour_name)
            results_frow.append(trip_id)

    return results_frow

def collect_results(result_list):
    return pd.DataFrame({'start_time': result_list[0::4],
                  'arrival_time': result_list[1::4],
                  'tour_id': result_list[2::4],
                  'trip_id': result_list[3::4]})


#######################################################################################################################


# if __name__ == '__main__':


    # Bring in the tours file that could not be processed in a vecotrized format
    temp_df1 = pd.read_csv(r"c:/personal/imm/start_time_parallel.csv")
    # get row purpose and direction to make unique column name for sampling from
    temp_df1['weight_column'] = temp_df1['trip_purpose'].astype(str) + '_' + temp_df1['direction'].astype(str)
    temp_df1['start_time'] = np.where(temp_df1['tour_seq'] == 0, temp_df1['tour_starttime'], 0)
    temp_df1['arrival_time'] = np.where(temp_df1['tour_seq'] == 0,
                                        temp_df1['tour_starttime'] + temp_df1['ttime_mins'] / 60, 0)
    print("Files batched in and the number of records are %s" %temp_df1.shape[0])

    temp_df1 = temp_df1.loc[temp_df1['tour_id'] < 500000]

    # bring in the time distribution dataframe
    time_dist = pd.read_csv(r"c:/personal/imm/start_time_distribution_treso_1.csv")
    time_dist_arr = np.array(time_dist.to_records())
    print("Time distribution batched in and converted to array")

    # set partial function to feed multiple arguments to Pool
    func_partial = partial(fun_array, time_dist_arr=time_dist_arr)
    pool = Pool(cpu_cores)

    # Start grouping
    start_time = timeit.default_timer()
    print("This is start time for grouping %s" % start_time)

    grp_list = []
    for name, group in temp_df1.groupby('tour_id'):
        grp_list.append(group)

    stop = timeit.default_timer()
    execution_time = stop - start_time
    print("End time of group creation %s" %execution_time)
#
#     start = timeit.default_timer()
#     print("This is start time for multiprocessing %s" % start_time)
#     with pool as p:
#         # result_list = p.map(func_partial, [group for name, group in grouped])
#         result_list = p.map(func_partial, grp_list)
#
#     # calculate script execution time
#     stop = timeit.default_timer()
#     execution_time = stop - start
#     print("End time for multiprocessing %s" %execution_time)
#
#     # make one list and then conver to dataframe
#     merged = list(itertools.chain(*result_list))
#     results_df = collect_results(merged)
#
#     print("Program Executed in %s seconds" %execution_time)  # It returns time in sec
#     print("")
# #
#     results_df.to_csv(r"c:/personal/imm/parallel_times.csv", index=False)
#
#
#     pool.close()
#     pool.join()

