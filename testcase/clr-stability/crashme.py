# !/usr/bin/python
#
# Copyright (C) 2014 Intel Corporation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# Author: ethan.gao@intel.com
# Date:   Aug 29, 2014
# Description: Crashme to testing the robustness of system operating environment.
#

import utils
import config
import subprocess as s
import unittest

CASENAME = 'crashme'
''' case name '''

SRCPKG = 'crashme-2.8.2.tar.gz'
''' specific source package with path ''' 

class Crashme(unittest.TestCase):

    def setUp(self):
        config.setup(CASENAME)
        config.prepareSrc(CASENAME, SRCPKG)
        config.buildBin(CASENAME)
        utils.logger.info("TESTCASE =====> %s <===== START" % CASENAME)
    
    def tearDown(self):
        config.back2Runner()
        utils.logger.info("TESTCASE =====> %s <===== END" % CASENAME)

    def crashme(self):
        try:
            s.check_call('crashme +2000 666 100 00:00:05', shell=True)
        except s.CalledProcessError:
            return False

        return True

    def test_crashme(self):
        self.assertTrue(self.crashme())

if __name__ == "__main__":
    unittest.main()
