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
# Description: fuzz system calls
#

import utils
import config
import subprocess as s
import unittest
import os

CASENAME = 'fuzz_syscalls'
''' case name '''

SRCPKG = "trinity-1.4.tar.xz"
''' specific source package with path '''

class FuzzSyscall(unittest.TestCase):

    def setUp(self):
        utils.logger.info("TESTCASE =====> %s <===== START" % CASENAME)
        config.setup(CASENAME)
        config.prepareSrc(CASENAME, SRCPKG)
        config.buildBin(CASENAME, cmdToBuild="./configure.sh && make all")

    def tearDown(self):
        config.back2Runner()
        utils.logger.info("TESTCASE =====> %s <===== END" % CASENAME)
    
    def trinity(self):
        try:
            s.check_call("sh scripts/test-all-syscalls-sequentially.sh", shell=True)
        except s.CalledProcessError:
            return False

        return True

    def test_trinity(self):
        self.assertTrue(self.trinity())

if __name__ == "__main__":
    unittest.main() 
