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
# Description: IO test emulated by utility iozone
#

import utils
import config
import subprocess as s
import unittest
import os

CASENAME = 'iozone'
''' case name '''

SRCPKG = None
''' source pacakge '''

class IOZone(unittest.TestCase):
	def setUp(self):
		utils.logger.info("TESTCASE =====> %s <===== START" % CASENAME)
		config.setup(CASENAME)
		config.prepareSrc(CASENAME, SRCPKG)
		config.buildBin(CASENAME, cmdToBuild='make linux-AMD64', subdir='src/current', cmdToInstall='manual', pkg2build=SRCPKG)

		utils.manualInstall('src/current', config.binDir())

	def tearDown(self):
		config.back2Runner()
		utils.logger.info("TESTCASE =====> %s <===== END" % CASENAME)
    
	def iozone(self):
		try:
			s.check_call("iozone -a", shell=True)
		except s.CalledProcessError:
			return False
		
		return True

	def test_iozone(self):
		self.assertTrue(self.iozone())

if __name__ == "__main__":
	unittest.main()

