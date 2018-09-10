import control_parameters
import common

logger = common.setupLogger("Start_Times_Assignment")

class EarlyValidation(object):

    def __init__(self):

        pass

    def validation(self):
        """


        :return:
        """

        EarlyValidFiles = control_parameters.EarlyValidFiles()
        csvfilelist = EarlyValidFiles.getCSVFileList()
        jsonfilelist = EarlyValidFiles.getJSONFileList()

        for file in csvfilelist:
            check_existence = common.file_existence(control_parameters.dirListing,file)
            logger.info("%s CSV files necessary to run the program found in the directory" % file)

            if not common.file_existence(control_parameters.dirListing, file):
                logger.info("%s CSV files necessary to run the program NOT found in the directory" % file)
                return False

        for file in jsonfilelist:
            check_existence = common.file_existence(control_parameters.dirListing, file)
            logger.info("%s JSON files necessary to run the program found in the directory" % file)

            if not common.file_existence(control_parameters.dirListing, file):
                logger.info("%s JSON files necessary to run the program NOT found in the directory" % file)
                return False

        return True