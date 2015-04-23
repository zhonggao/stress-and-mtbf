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
# Description: Stress test for SSH.
#

import utils
import config
import subprocess as s
import unittest
import os

CASENAME = 'sshstress'
''' case name '''

SRCPKG = None
''' specific source package with path ''' 

REQUIREDPKGS = {'expect':'package'}

class SSHStress(unittest.TestCase):
	def setUp(self):
		utils.logger.info("TESTCASE =====> %s <===== START" % CASENAME)
		utils.requiredPkgs('zypper', REQUIREDPKGS)
		config.setup(CASENAME)

	def tearDown(self):
		config.back2Runner()
		utils.logger.info("TESTCASE =====> %s <===== END" % CASENAME)

	def sshstress(self):
		try:
			os.system("cp %s/%s %s" % (config.binDir(), 'ssh.expect', config.caseDir(CASENAME)))
			SSHSERVER = config.testcaseAttr(CASENAME,"sshserver")
			USER = config.testcaseAttr(CASENAME,"user")
			PASSWORD = config.testcaseAttr(CASENAME,"password")
			s.check_call("sh -c 'expect ssh.expect %s %s %s'" % (SSHSERVER,USER,PASSWORD), shell=True)
		except s.CalledProcessError:
			return False
		
		return True

	def test_sshstress(self):
		self.assertTrue(self.sshstress())

if __name__ == "__main__":
	unittest.main()
