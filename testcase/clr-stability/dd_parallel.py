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
# Description: r/w raw data and file in parallel(at least greater than 1G).
#

import os
import sys
import utils
import config
import subprocess as s
import unittest

CASENAME = 'dd_parallel'
''' case name '''

SRCPKG = None
''' specific source package with path ''' 

class DDParallel(unittest.TestCase):
	def setUp(self):
		config.setup(CASENAME)
		utils.logger.info("TESTCASE =====> %s <===== START" % CASENAME)

	def tearDown(self):
		config.back2Runner()
		utils.logger.info("TESTCASE =====> %s <===== END" % CASENAME)

	def file_write(self):
	
		p = []
		
		try:
			for i in range(5):
				filename = "file.%d" % i
				SIZE = int(config.testcaseAttr(CASENAME,'datasize'))
				dd = 'dd if=/dev/zero of=%s bs=4k count=%d' % (filename, SIZE)
				p.append(s.Popen(dd, shell=True))

			for i in range(5):
				sys.stdout.flush()
				os.waitpid(p[i].pid, 0)

			sys.stdout.flush()
			sys.stderr.flush()

		except (OSError, ValueError, s.CalledProcessError):
			return False
		
		return True

	def file_read(self, sequential=True):

		p = []

		self.file_write()

		try:
			for i in range(5):
				filename = "file.%d" % i
				SIZE = int(config.testcaseAttr(CASENAME,'datasize'))
				dd = 'dd if=%s of=/dev/null bs=4k count=%d' % (filename, SIZE)
			
				if sequential:
					s.check_call(dd, shell=True)
				else:
					p.append(s.Popen(dd, shell=True))

				if not sequential:
					for i in range(5):
						sys.stdout.flush()
						os.waitpid(p[i].pid, 0)
			
		except (OSError,s.CalledProcessError, ValueError):
			return False

		return True

	def raw_write(self):
		pass

	def raw_read(self):
		pass

	def test_raw_write(self):
		pass

	def test_raw_read(self):
		pass

	def test_file_write(self):
		self.assertTrue(self.file_write())

	def test_file_read(self):
		self.assertTrue(self.file_read())

if __name__ == "__main__":
	unittest.main()
