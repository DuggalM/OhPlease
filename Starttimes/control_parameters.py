from multiprocessing import Pool, cpu_count
from numpy.random import RandomState


# set random generator and get the number of cores
prng = RandomState(123)
seed = 12345
cpu_cores = cpu_count()-6
logname = "start_times.log"

dirListing = "c:\\projects\\treso\\start_times\\"

# EARLY VALIDATION FILES
class EarlyValidFiles(object):
    TOURS_OUT = 'tours_out.gz'
    TRIPS_OUT = 'trips_out.gz'
    TTIMES = 'ff_ttimes.gz'
    TIME_DIST = 'start_time_distribution_treso_1.csv'
    DTYPE_TRESO_TRIPS = 'dtype_treso_trips.json'
    DTYPE_SOV_TIMES = 'dtype_SOVNT_times.json'


    @classmethod
    def getJSONFileList(cls):
        return [
            cls.DTYPE_TRESO_TRIPS, cls.DTYPE_SOV_TIMES]

    @classmethod
    def getCSVFileList(cls):
        return [cls.TOURS_OUT, cls.TRIPS_OUT, cls.TTIMES, cls.TIME_DIST]



