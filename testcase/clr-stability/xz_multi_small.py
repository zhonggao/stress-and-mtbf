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
# Description: Compress a great many of small files with xz.
#

import utils
import config
import subprocess as s
import unittest
import os


CASENAME = 'xz_multi_small'
''' case name '''

SRCPKG = "linux-3.16.1.tar.xz"
''' specific source package with path ''' 

class XZMultiSmall(unittest.TestCase):
	def setUp(self):
		utils.logger.info("TESTCASE =====> %s <===== START" % CASENAME)
		config.setup(CASENAME)
		config.prepareSrc(CASENAME, SRCPKG)

	def tearDown(self):
		config.back2Runner()
		utils.logger.info("TESTCASE =====> %s <===== END" % CASENAME)

	def iterate_xz_files(self,path = None):
		if path is None:
			path = os.getcwd()

		for f in os.listdir(path):
			if utils.isfile(f):
				s.check_call('xz -zkv %s' % f, shell=True)
			elif utils.isDir(f):
				subdir = path + '/' + f
				os.chdir(f)
				self.iterate_xz_files(subdir)
				os.chdir(path)
			else:
				utils.logger.error("Error: Unknown file or directory type")
				return False

		return True	

	def xz_multi_files(self):
		if os.path.basename(os.getcwd()) != utils.codeIn(None,SRCPKG):
			utils.logger.error("Error: xz with incorrect source")
			return False	

		try:
			if not self.iterate_xz_files():
				return False
		except (OSError, s.CalledProcessError):
			return False
			
		return True

	def test_xz_multi_files(self):
		self.assertTrue(self.xz_multi_files())


if __name__ == "__main__":
	unittest.main()
