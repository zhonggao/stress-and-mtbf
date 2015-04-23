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
# Description: Stress test for HTTP.
#

import utils
import config
import subprocess as s
import unittest
import os

CASENAME = 'httpstress'
''' case name '''

SRCPKG = None
''' specific source package with path ''' 

class HTTPStress(unittest.TestCase):

	def setUp(self):
		config.setup(CASENAME)
		utils.logger.info("TESTCASE =====> %s <===== START" % CASENAME)

	def tearDown(self):
		config.back2Runner()
		utils.logger.info("TESTCASE =====> %s <===== END" % CASENAME)
    
	def httpstress(self):
		try:
			IMAGE_VERSION = s.check_output('cat /etc/ImageVersion', shell=True)
			IMAGE_DATE = IMAGE_VERSION.split('-')[2].strip()
			HTTPSERVER = config.testcaseAttr(CASENAME, 'httpserver')
			FILE_TO_GET = HTTPSERVER + "clr-generic.x86_64-%s.manifest.xml" % IMAGE_DATE
			s.check_call("curl -O %s -x %s -v" % (FILE_TO_GET, config.NWProxy()), shell=True)
		except s.CalledProcessError:
			return False

		if not os.path.exists("clr-generic.x86_64-%s.manifest.xml" % IMAGE_DATE):
			return False

		return True

	def test_httpstress(self):
		self.assertTrue(self.httpstress())

if __name__ == "__main__":
    unittest.main()
