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
# Description: Compress a file greater than 4G via xz.
#

import utils
import config
import subprocess as s
import unittest
import os


CASENAME = 'xz_single_huge'
''' case name '''

SRCPKG = None
''' specific source package with path ''' 

class XZSingleHuge(unittest.TestCase):

	def setUp(self):
		utils.logger.info("TESTCASE =====> %s <===== START" % CASENAME)
		config.setup(CASENAME)

	def tearDown(self):
		config.back2Runner()
		utils.logger.info("TESTCASE =====> %s <===== END" % CASENAME)

	def xz_single_huge(self):
		try:
			s.check_call("dd if=/dev/zero of=xz_single_huge.raw bs=4k count=1048576", shell=True)
			s.check_call('xz -zvk xz_single_huge.raw', shell=True)
		except s.CalledProcessError:
			return False

		if os.path.exists('xz_single_huge.raw.xz'):
			return True
		else:
			return False

	def test_xz_single_huge(self):
		self.assertTrue(self.xz_single_huge())

if __name__ == "__main__":
	unittest.main()
