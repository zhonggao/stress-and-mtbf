# !/usr/bin/python

# Copyright (C) 2014 Intel Corporation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# Author: ethan.gao@intel.com
# Date: Sep 9, 2014
# Description: Stress given subsystems under a specified load.
#

import utils
import config
import subprocess as s
import unittest
import os


CASENAME = 'sysstress'
''' case name '''

SRCPKG = "stress-1.0.4.tar.gz"
''' specific source package with path ''' 

class SysStress(unittest.TestCase):

    def setUp(self):
        utils.logger.info("TESTCASE =====> %s <===== START" % CASENAME)
        config.setup(CASENAME)
        config.prepareSrc(CASENAME, SRCPKG)
        config.buildBin(CASENAME, cmdToBuild="./configure --prefix=%s && make all"% config.binDir(), cmdToInstall="make install")

	# FIXME: sub-dirs can not be searched in clr
	os.system("mv %s/bin/* %s" % (config.binDir(), config.binDir()))

    def tearDown(self):
        config.back2Runner()
        utils.logger.info("TESTCASE =====> %s <===== END" % CASENAME)

    def sysstress(self):
        try:
            s.check_call("stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M --timeout 10s", shell=True)
        except s.CalledProcessError:
            return False

        return True

    def test_sysstress(self):
        self.assertTrue(self.sysstress())


if __name__ == "__main__":
    unittest.main()
