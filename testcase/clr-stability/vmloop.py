# !/usr/bin/python
# Copyright (C) 2014 Intel Corporation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# Author: ethan.gao@intel.com
# Date:   Sept 5, 2014
# Description: start n virtual machines at the same time
#

import utils
import config
import subprocess as s
import unittest

CASENAME = 'vmloop'
SRCPKG = 'vmstart.tar.xz'
REQUIREDPKGS = {'multipath-tools':'package', 'rsync':'package', 'qemu':'package'}

class VMloop(unittest.TestCase):
	def setUp(self):
		utils.logger.info("TESTCASE =====> %s <===== START" % CASENAME)
		utils.requiredPkgs(package=REQUIREDPKGS)
		config.setup(CASENAME)
		config.prepareSrc(CASENAME, SRCPKG)
		config.buildBin(CASENAME, pkg2build = SRCPKG)

	def tearDown(self):
		config.back2Runner()
		utils.logger.info("TESTCASE =====> %s <===== END" % CASENAME)

	def vm_loop_start(self):
		num_to_start = config.testcaseAttr(CASENAME, 'vms')
		mem_for_each = config.testcaseAttr(CASENAME, 'memory')

		resourceNeeded = config.resourceName(CASENAME)
		resourceNeeded = utils.codeIn(None,resourceNeeded)

		args = dict([('resource', resourceNeeded), ('vms', num_to_start), ('memory', mem_for_each)])
		
		try:
			utils.logger.info("Intend to start %s VMs with %s memory for each"% (num_to_start, mem_for_each))
			config.runScript(CASENAME, args)
		except s.CalledProcessError:
			return False

		return True

	def test_vm_loop_start(self):
		self.assertTrue(self.vm_loop_start())

if __name__ == "__main__":
	unittest.main()
		
		
