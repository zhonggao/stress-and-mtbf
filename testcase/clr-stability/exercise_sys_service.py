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
# Description: exercise system services
#
import random
import utils
import config
import subprocess as s
import unittest
import os

CASENAME = 'exercise_sys_service'
''' case name '''

SRCPKG = None
''' specific source package with path '''

ACTIONS = ['stop','enable','reload','disable','start', 'try-restart','reenable', 'kill','restart','status']

class SysServiceExercise(unittest.TestCase):
	def setUp(self):
		config.setup(CASENAME)
		utils.logger.info("TESTCASE =====> %s <===== START" % CASENAME)

	def tearDown(self):
		config.back2Runner()
		utils.logger.info("TESTCASE =====> %s <===== END" % CASENAME)
		
	def exercise_sys_services(self):
		SERVICES = []

		optSeed = range(len(ACTIONS))
		random.shuffle(optSeed)

		SERVICES = s.check_output("systemctl -t service | grep '.service' | awk '{print $1}'", shell=True).strip().split('\n')

		for service in SERVICES:
			if "sshd" in service or "systemd-networkd" in service or "systemd-journald" in service:
				continue

			for opt in optSeed:
				try:
					utils.logger.info("SERVICE === %s ######### OPERATION === %s" % (service,ACTIONS[opt]))
					os.system("systemctl %s %s" % (ACTIONS[opt], service))
				except (OSError,SystemError,ValueError):
					return False

		return True

	def test_exercise_sys_services(self):
		self.assertTrue(self.exercise_sys_services())

if __name__ == "__main__":
	unittest.main()
