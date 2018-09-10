import pandas as pd
import numpy as np
import subprocess
import os
import control_parameters

class LaunchingMlogit(object):



    ctl_pk_files = ['hbw_peak_treso.ctl', 'hbu_peak_treso.ctl', 'hbs_peak_treso.ctl', 'hbo_peak_treso.ctl',
                       'hbm_peak_treso.ctl', 'wbo_peak_treso.ctl', 'nhb_peak_treso.ctl']

    ctl_offpk_files = ['hbw_offpeak_treso.ctl', 'hbu_offpeak_treso.ctl', 'hbs_offpeak_treso.ctl', 'hbo_offpeak_treso.ctl',
                       'hbm_offpeak_treso.ctl', 'wbo_offpeak_treso.ctl', 'nhb_offpeak_treso.ctl']


    mlogit_options = {"   TRNEGR=F\n":"   TRNEGR=T\n",
                      "   UBERMODE=F\n":"   UBERMODE=T\n",
                      "   AVMDL=F\n":"   AVMDL=T\n",
                      "   TRESO=F\n":"   TRESO=T\n",
                      "   UBERTRN=F\n":"   UBERTRN=T\n"}

    avlmdl ="   FAVCVPROP='sample_veh_proportions_gghm_zone_csd.csv'    !AV/CV Proportion File (AVMDL=T)"


    def check_av_file(self, path, file, avlmdl):
        """

        """

        f = open(os.path.join(path, file), "r")
        data = f.readlines()
        f.close()
        line_16 = data[16]
        if line_16 == '&END\n':
            data.insert(16, avlmdl)

            f = open(os.path.join(path, file), "w")
            data = "".join(data)
            f.write(data)
            f.close()

    def set_file_options(self, path, file, key, value):
        """

        """
        f = open(os.path.join(path, file))
        filedata = f.read()
        f.close()
        newdata = filedata.replace(key, value)
        f = open(os.path.join(path, file), 'w')
        f.write(newdata)
        f.close()


    def runner_mlogit(self):


        # set the necessary options to run MLOGIT for Discretization
        for file in self.ctl_pk_files:

            self.check_av_file(control_parameters.dirListing_mlogit_controls, file, self.avlmdl)

            for key, value in self.mlogit_options.items():
                self.set_file_options(control_parameters.dirListing_mlogit_controls, file, key, value)

        for file in self.ctl_offpk_files:

            self.check_av_file(control_parameters.dirListing_mlogit_controls, file, self.avlmdl)

            for key, value in self.mlogit_options.items():
                self.set_file_options(control_parameters.dirListing_mlogit_controls, file, key, value)

        for file in self.ctl_pk_files:

            t = subprocess.run(["MLOGIT.exe", file], cwd=control_parameters.dirListing_mlogit_controls,
                               shell=True, stdout=subprocess.PIPE)
            control_parameters.logger.info( "%s processed " %file)

        for file in self.ctl_offpk_files:
            t = subprocess.run(["MLOGIT.exe", file], cwd=control_parameters.dirListing_mlogit_controls,
                               shell=True, stdout=subprocess.PIPE)
            control_parameters.logger.info("%s processed " % file)


