import control_parameters
import common
import pandas as pd
import validation
import numpy as np
from numpy.random import RandomState
from numpy.random import choice
import os


class StartTimesCreate(object):

    """


    """

    def __init__(self, prng):

        self.prng = prng
        pass


    def clean_dataframe(self, trips_df, tour_df, sov_times_df):
        """

        :param trips_df:
        :param sov_times_df:
        :return: temp_df
        """

        # clean the tours and attach tour_id to trips
        tour_df = tour_df[['tour_id', 'start_time']].copy()
        tour_df.rename(columns={'start_time': 'tour_starttime'}, inplace=True)
        trips_df = pd.merge(trips_df, tour_df, on='tour_id')

        # Get rid of negative zone numbers
        mask = trips_df[(trips_df['origin_zone'] == -1) | (trips_df['destination_zone'] == -1)]
        temp_df = trips_df.loc[~trips_df['tour_id'].isin(mask['tour_id'])]
        validation.logger.info("There are a total of %s trips for which a start time is to be "
                               "allocated" %temp_df.shape[0])

        # Assign the number of tours generated by a person as well as the trips within each tour. This will
        # be used to slice the dataframe for vectorized operations
        tour_counts = temp_df.groupby(['hhid', 'pid'])['tour_id'].nunique().reset_index(name="num_tours")
        trip_counts = temp_df.groupby(['hhid', 'pid', 'tour_id']).size().reset_index(name="trips_tour")

        temp_df = pd.merge(temp_df, tour_counts, on=['hhid', 'pid']).merge(trip_counts, on=['hhid', 'pid', 'tour_id'])
        # sorting order for sure if you want TOD to work, period.
        temp_df.sort_values(['hhid', 'pid', 'tour_id', 'tour_seq'], inplace=True)

        # Clean the sov time dataframe. This is the SOV NonToll times
        ttime_df = sov_times_df
        ttime_df.rename(columns={'0187474001524615141/': 'origin_zone'}, inplace=True)
        ttime_df = pd.melt(ttime_df, id_vars=["origin_zone"]).dropna()
        ttime_df.rename(columns={'variable': 'destination_zone', 'value': 'ttime_mins'}, inplace=True)

        return (temp_df, ttime_df)


    def reduce_memory(self, temp_df, ttime_df):
        """

        :param temp_df:
        :param ttime_df:
        :return:
        """

        # set dictionary of Dtypes to reduce size requirement of travel time dataframe
        dtype_temp_df = {}
        dtype_defs = common.dtype_defintions(control_parameters.dirListing,
                                             control_parameters.EarlyValidFiles.getJSONFileList())
        dtype_temp_df = dtype_defs[control_parameters.EarlyValidFiles.DTYPE_TRESO_TRIPS]
        dtype_ttime_df = dtype_defs[control_parameters.EarlyValidFiles.DTYPE_SOV_TIMES]

        # save some memory
        temp_df.drop(['is_virtual', 'trip_km'], axis=1, inplace=True)

        for key, value in dtype_ttime_df.items():
            ttime_df[key] = ttime_df[key].astype(value)

        for key, value in dtype_temp_df.items():
            temp_df[key] = temp_df[key].astype(value)

        validation.logger.info("Dtypes for the trips file are reset to reduce the memory footprint")

        return (temp_df, ttime_df)


    def assign_trip_purpose(self, temp_df):
        """

        :param temp_df:
        :return:
        """

        # Home in one trip end
        temp_df['trip_purpose'] = "NHB"

        temp_df.loc[((temp_df['origin_activity'].isin(["home", "work"]) & (
        temp_df['destination_activity'].isin(["home", "work"])))), 'trip_purpose'] = "HBW"
        temp_df.loc[((temp_df['origin_activity'].isin(["home", "school"]) & (
        temp_df['destination_activity'].isin(["home", "school"])))), 'trip_purpose'] = "HBS"
        temp_df.loc[((temp_df['origin_activity'].isin(["home", "university"]) & (
        temp_df['destination_activity'].isin(["home", "university"])))), 'trip_purpose'] = "HBU"
        temp_df.loc[((temp_df['origin_activity'].isin(["home", "other", "business"]) & (
        temp_df['destination_activity'].isin(["home", "other", "business"])))), 'trip_purpose'] = "HBO"
        temp_df.loc[((temp_df['origin_activity'].isin(["home", "shop"]) & (
        temp_df['destination_activity'].isin(["home", "shop"])))), 'trip_purpose'] = "HBM"
        temp_df.loc[((temp_df['origin_activity'].isin(["home", "escort"]) & (
        temp_df['destination_activity'].isin(["home", "escort"])))), 'trip_purpose'] = "HBE"

        temp_df.loc[((temp_df['origin_activity'].isin(["work"]) & (
                temp_df['destination_activity'] != "home"))), 'trip_purpose'] = "WBO"
        temp_df.loc[((temp_df['origin_activity'] != "home") & (
        temp_df['destination_activity'].isin(["work"]))), 'trip_purpose'] = "WBO"

        temp_df['trip_purpose'] = temp_df['trip_purpose'].astype('object')

        return temp_df

    def assign_dir(self, temp_df):
        """

        :param temp_df:
        :return:
        """
        # Add in direction. It is outbound if the origin_activity has 'home' in it and inbound if 'home' is in the destination_activity.
        # Further, because the NHBO is directionless, at least w.r.t to the home, they have been all assigned inbound as
        # the distributions in the start time file are the same for inbound and outbound for these the NHBO trip purpose.
        # The NHBW is treated the same as the WBO trip purpose from the GGHM and if there is 'work' in the origin_activity it gets
        # an outbound and inbound if 'work' is in the destination_activity.
        # Finally, Business to Business is assigned a direction randomly.

        # Home in one trip end
        temp_df['direction'] = np.nan
        temp_df.loc[(temp_df['origin_activity'] == 'home'), 'direction'] = 'outbound'
        temp_df.loc[
            (temp_df['direction'].isnull()) & (temp_df['destination_activity'] == 'home'), 'direction'] = 'inbound'

        # NHBO
        temp_df.loc[(temp_df['trip_purpose'] == 'NHBO'), 'direction'] = 'inbound'

        # NHBW
        temp_df.loc[(temp_df['direction'].isnull()) & (temp_df['origin_activity'] == 'work'), 'direction'] = 'outbound'
        temp_df.loc[
            (temp_df['direction'].isnull()) & (temp_df['destination_activity'] == 'work'), 'direction'] = 'inbound'

        # Business, randomly select 50% of the records that were yet NAN and give them outbound with the
        # rest as inbound
        random_direction = temp_df[temp_df['direction'].isnull()].sample(frac=0.5, random_state=control_parameters.seed)
        temp_df.loc[(temp_df.index.isin(random_direction.index)), 'direction'] = 'outbound'
        temp_df.loc[(temp_df['direction'].isnull()), 'direction'] = 'inbound'

        temp_df['direction'] = temp_df['direction'].astype('object')

        return temp_df

    def calculate_starttimes_two_trips(self, temp_df, ttime_df, time_dist_df):
        """

        :param temp_df:
        :param ttime_df:
        :return:
        """

        # Transfer O-D level SOV-NT auto travel times
        temp_df = pd.merge(temp_df, ttime_df, how='left', on=['origin_zone', 'destination_zone'])

        # get the dataframe where only two trips take place in a tour
        two_trips_df = temp_df.copy()
        two_trips_df = two_trips_df.loc[two_trips_df['trips_tour'] == 2]

        # set defaults
        two_trips_df['start_time'] = 99
        two_trips_df['arrival_time'] = 99
        two_trips_df.loc[(two_trips_df['tour_seq'] == 0), 'start_time'] = two_trips_df['tour_starttime']
        two_trips_df.loc[(two_trips_df['tour_seq'] == 0), 'arrival_time'] = two_trips_df['tour_starttime'] + \
                                                                            two_trips_df['ttime_mins'] / 60
        two_trips_df['arrival_hr'] = two_trips_df['arrival_time'].astype(int)

        # get the first trip of every tour
        first_trip_only_df = two_trips_df.loc[two_trips_df['tour_seq'] == 0]
        segments = first_trip_only_df.groupby(['trip_purpose', 'direction', 'arrival_hr']).size().\
            reset_index(name="counts")

        # reset direction as the second trip is by default coming home
        segments['direction'] = 'inbound'
        start_times = []
        for i in range(0, segments.shape[0]):

            purp = segments.at[segments.index[i], 'trip_purpose']
            direction = segments.at[segments.index[i], 'direction']
            weight_column = purp + '_' + direction

            arrival_hr = segments.at[segments.index[i], 'arrival_hr']
            num_sample = segments.at[segments.index[i], 'counts']

            if arrival_hr < 24:

                time_dist1 = time_dist_df.loc[time_dist_df['Time'] >= arrival_hr]
                sampled_times = time_dist1.sample(n = num_sample, weights=time_dist1[weight_column], replace=True,
                                                  random_state=control_parameters.prng)

                s1 = sampled_times['Time'].values
                s1 = pd.DataFrame(s1, columns=['start_time'])

                tourid_ls = two_trips_df.loc[
                    (two_trips_df['trip_purpose'] == purp) & (two_trips_df['arrival_hr'] == arrival_hr)]
                tourid_ls = tourid_ls['tour_id'].tolist()

                index_concat = two_trips_df.loc[
                    (two_trips_df['tour_id'].isin(tourid_ls)) & (two_trips_df['tour_seq'] == 1)].index.tolist()
                index_concat = pd.DataFrame(index_concat, columns=['index'])
                index_concat['index'] = index_concat['index'].astype(int)

                s1 = pd.concat([s1, index_concat], axis = 1).set_index('index')
                two_trips_df.loc[s1.index, s1.columns] = s1

            else:
                validation.logger.info("trip spills to early morning and will be fixed separately")

        two_trips_df['arrival_time'] = two_trips_df['start_time'] + two_trips_df['ttime_mins'] / 60
        two_trips_df = two_trips_df[['trip_id', 'tour_id', 'start_time', 'arrival_time']]

        return (temp_df, two_trips_df)

    def prepare_two_trips_more_df(self, temp_df, two_trips_df):
        """

        :param temp_df:
        :param two_trips_df:
        :return:
        """

        # only keep the records that are left over after analyzing tours with only 2 trips
        temp_df1 = temp_df.copy()
        temp_df1 = temp_df1.loc[~temp_df1['tour_id'].isin(two_trips_df['tour_id'])]

        # get row purpose and direction to make unique column name for sampling from
        # temp_df1['weight_column'] = temp_df1['trip_purpose'].astype(str) + '_' + temp_df1['direction'].astype(str)
        # temp_df1['start_time'] = np.where(temp_df1['tour_seq'] == 0, temp_df1['tour_starttime'], 0).copy()
        temp_df1.loc[:, 'weight_column'] = temp_df1['trip_purpose'].astype(str) + '_' + temp_df1['direction'].astype(str)
        temp_df1.loc[temp_df1['tour_seq'] == 0, 'start_time'] = temp_df1['tour_starttime']
        temp_df1.loc[temp_df1['tour_seq'] > 0, 'start_time'] = 0
        temp_df1.loc[temp_df1['tour_seq'] == 0, 'arrival_time'] = temp_df1['tour_starttime'] + \
                                                                  temp_df1['ttime_mins'] / 60
        temp_df1.loc[temp_df1['tour_seq'] > 0, 'arrival_time'] = 0

        # change dtypes of categorical columns to object
        msk = temp_df1.columns[temp_df1.dtypes.eq('category')]
        if len(msk)>0:
            temp_df1[msk] = temp_df1[msk].astype('object')

        return temp_df1


    def calculate_starttimes_morethan_twotrips(self, group, time_dist_arr):
        """

        :param temp_array:
        :param time_dist_arr:
        :return:
        """
        prng = self.prng
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

                if time_dist1_arr.shape[0] > 0:

                    probs = time_dist1_arr[weight_column]
                    probs = probs / probs.sum()
                    start_time = choice(time_dist1_arr['Time'], size=1, p=probs, replace=True)
                    start_time = start_time[0]
                else:
                    start_time = results_frow[-3]

                newarrival_time = start_time + temp_array[i][
                    'ttime_mins'] / 60  ### calculate the arrival time by adding start time to the travel time
                results_frow.append(start_time)
                results_frow.append(newarrival_time)
                results_frow.append(tour_name)
                results_frow.append(trip_id)

        return results_frow


    def run(self):

        # run eager validation of files
        validation.EarlyValidation().validation()
        validation.logger.info("Validation completed")

        # batch in the files
        tour_df = pd.read_csv(os.path.join(control_parameters.dirListing,
                                           control_parameters.EarlyValidFiles.TOURS_OUT), compression='gzip', sep=',')
        trips_df = pd.read_csv(os.path.join(control_parameters.dirListing,
                                            control_parameters.EarlyValidFiles.TRIPS_OUT), compression='gzip', sep=',')
        sov_times_df = pd.read_csv(os.path.join(control_parameters.dirListing,
                                                control_parameters.EarlyValidFiles.TTIMES), compression='gzip', sep=',')
        time_dist_df = pd.read_csv(os.path.join(control_parameters.dirListing,
                                                control_parameters.EarlyValidFiles.TIME_DIST))

        # Now run multiprocessing on the tours with more than two trips in them
        time_dist_arr = np.array(time_dist_df.to_records())

        # Call the sequence of functions
        temp_df, ttime_df = self.clean_dataframe(trips_df, tour_df, sov_times_df)
        validation.logger.info("Tour information and travel time information attached to the trips dataframe.")
        temp_df, ttime_df = self.reduce_memory(temp_df, ttime_df)
        validation.logger.info("Appropriate dtypes attached to reduce memory requirements.")
        temp_df = self.assign_trip_purpose(temp_df)
        validation.logger.info("Trip purpose assigned to the trips dataframe.")
        temp_df = self.assign_dir(temp_df)
        validation.logger.info("Trip direction assigned.")
        temp_df_fin, two_trips_df = self.calculate_starttimes_two_trips(temp_df, ttime_df, time_dist_df)
        validation.logger.info("Start times assigned to all the tours that have only two trips in it.")

        return (temp_df_fin, two_trips_df, time_dist_arr)