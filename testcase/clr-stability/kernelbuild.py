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
# Description: Stress on kernel compiling.
#

import utils
import config
import subprocess as s
import unittest

CASENAME = 'kernelbuild'
''' case name '''

SRCPKG = None
''' specific source package with path ''' 

REQUIREDPKGS = {'bc':'package', 'ncurses':'package'}
''' required system tools or packages during test '''

class KernelBuild(unittest.TestCase):

	def setUp(self):
		utils.logger.info("TESTCASE =====> %s <===== START" % CASENAME)
		utils.requiredPkgs(package=REQUIREDPKGS)
		config.setup(CASENAME)	
		config.prepareSrc(CASENAME, SRCPKG)
		config.buildBin(CASENAME)
	
	def tearDown(self):
		config.back2Runner()
		utils.logger.info("TESTCASE =====> %s <===== END" % CASENAME)
	
	def kernel_build(self):
		try:
			utils.logger.info('Start to build kernel and please expect certain minutes or logger to finish...')
			s.check_call('make mrproper', shell=True)
			s.check_call('make defconfig', shell=True)
			s.check_call('make -j4 bzImage', shell=True)
		except s.CalledProcessError:
			return False

		return True

	def test_kernel_build(self):
		self.assertTrue(self.kernel_build())

if __name__ == "__main__":
	unittest.main()

