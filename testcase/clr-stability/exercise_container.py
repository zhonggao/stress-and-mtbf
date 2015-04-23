# !/usr/bin/python
# coding: utf-8

# Copyright (C) 2014 Intel Corporation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# Author: yileix.wan@intel.com
# Date: Sep 9, 2014
# Description: Bring up and down containers iteratively.
#

import utils
import config
import subprocess as s
import unittest
import os

CASENAME = 'exercise_container'
''' case name '''

SRCPKG = None
''' specific source package with path '''

REQUIREDPKGS = {'clr-bootstrap': 'package'}

class ContainerExercise(unittest.TestCase):
	def setUp(self):
		utils.requiredPkgs('zypper', REQUIREDPKGS)
		config.setup(CASENAME)
		utils.logger.info("TESTCASE =====> %s <===== START" % CASENAME)

	def tearDown(self):
		config.back2Runner()
		utils.logger.info("TESTCASE =====> %s <===== END" % CASENAME)
    
	def exercise_container(self):
		try:
			REPO = config.testcaseAttr(CASENAME, 'repo')
			s.check_call('/usr/bin/clr-bootstrap -d containers -r ' + REPO + ' -e "irssi wget" -n', shell=True)
		except s.CalledProcessError:
			return False

		if not os.path.exists('containers'):
			return False

		return True

	def test_exercise_container(self):
		self.assertTrue(self.exercise_container())

if __name__ == "__main__":
	unittest.main()
