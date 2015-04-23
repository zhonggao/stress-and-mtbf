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
# Description: system stability and performance by calculating millions of digits of Pi
#

import utils
import config
import subprocess as s
import unittest
import os


CASENAME = 'systester'
''' case name '''

SRCPKG = "systester-1.5.1-linux-amd64.tar.xz"
''' specific source package with path ''' 

class SysTester(unittest.TestCase):

    def setUp(self):
        utils.logger.info("TESTCASE =====> %s <===== START" % CASENAME)
        config.setup(CASENAME)
        config.prepareSrc(CASENAME, SRCPKG)
        config.buildBin(CASENAME)

    def tearDown(self):
        config.back2Runner()
        utils.logger.info("TESTCASE =====> %s <===== END" % CASENAME)

    def systester(self):
        try:
            #s.check_call("systester-cli -gausslg 64M -threads 8 -bench", shell=True)
            s.check_call("systester-cli -gausslg 1M -threads 8 -bench", shell=True)	    
        except s.CalledProcessError:
            return False
    
        return True

    def test_systester(self):
        self.assertTrue(self.systester())

if __name__ == "__main__":
    unittest.main()
