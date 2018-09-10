import pandas as pd
import numpy as np
import time
from functools import partial
import starttimes
from multiprocessing import Pool, cpu_count
from numpy.random import RandomState

cpu_cores = cpu_count()
prng = RandomState(123)


temp_df1 = pd.read_csv(r"c:/projects/treso/start_times/temp_df1.csv")
# time_dist = pd.read_csv(r"c:/personal/imm/start_time_distribution_treso_1.csv")
# # get row purpose and direction to make unique column name for sampling from
# temp_df1['weight_column'] = temp_df1['trip_purpose'].astype(str) + '_' + temp_df1['direction'].astype(str)
# temp_df1['start_time'] = np.where(temp_df1['tour_seq'] == 0, temp_df1['tour_starttime'],0)
# temp_df1['arrival_time'] = np.where(temp_df1['tour_seq'] == 0, temp_df1['tour_starttime'] + temp_df1['ttime_mins']/60,0)


# temp_df2 = temp_df1.loc[temp_df1['tour_id'] < 50000]
# print(temp_df2.shape[0])

start_time = time.time()

grp_list = []
for name, group in temp_df1.groupby('tour_id'):
    grp_list.append(group)

print ("time elapsed: {:.2f}s".format(time.time() - start_time))
