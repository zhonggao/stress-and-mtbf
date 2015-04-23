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
# Description: Stress network performance test via netperf.
#

import time
import signal
import utils
import config
import subprocess as s
import unittest
import os

CASENAME = 'netperf'
''' case name '''

SRCPKG = "netperf-2.6.0.tar.gz"
''' specific source package with path ''' 

REQUIREDPKGS = {'expect': 'package'}

class NetPerf(unittest.TestCase):
	def setUp(self):
		utils.logger.info("TESTCASE =====> %s <===== START" % CASENAME)
		utils.requiredPkgs('zypper', REQUIREDPKGS)
		config.setup(CASENAME)
		config.prepareSrc(CASENAME, None)
		config.buildBin(CASENAME, cmdToBuild="./configure --prefix=%s && make all" % config.binDir(), cmdToInstall="make install")

		# FIXME system bug - dont's search subdir underneath $PATH
		os.system("cp -v %s/%s %s" % (config.binDir(), "bin/*", config.binDir()))

		# prepare and start netserver 
		self.process = self.prepareNetServer()

	def tearDown(self):
		# To avoid child process to be defunct state aka. Zombie
		os.waitpid(self.process.pid, 0)

		config.back2Runner()
		utils.logger.info("TESTCASE =====> %s <===== END" % CASENAME)

	def prepareNetServer(self):
		SERVER = config.testcaseAttr(CASENAME, 'net_server')
		USER = config.testcaseAttr(CASENAME, 'user')
		PASSWD = config.testcaseAttr(CASENAME, 'passcode')
		SOURCE = config.pkgsDir() + '/' + SRCPKG
		SCRIPT = "netserver.sh"

		os.system("cp -v %s/%s %s" % (config.binDir(), 'netserver.*', utils.codeIn(config.srcDir(CASENAME), SRCPKG)))
		process = s.Popen("sh -c 'expect netserver.expect %s %s %s %s %s'" % (SERVER, USER, PASSWD, SOURCE, SCRIPT), shell=True)
		
		return process
	
	def terminate_server(self):
		self.process.terminate()


	def netperf(self):
		clientCmd = None
		localIP = "127.0.0.1"

		#self.prepareNetServer()
		time.sleep(15)

		TESTS = ['TCP_STREAM', 'TCP_CC', 'TCP_RR', 'TCP_CRR', 'UDP_STREAM', 'UDP_RR']
		server = config.testcaseAttr(CASENAME, 'net_server')
		duration = config.testcaseAttr(CASENAME, 'duration')

		NETDEVS=s.check_output("ip addr show | grep -iw inet | awk '{print $2}' | cut -d '/' -f1", shell=True).split('\n')
		for ip_addr in NETDEVS:
			if ip_addr == '127.0.0.1' or ip_addr == '':
				continue
			else:
				localIP = ip_addr
			
		try:
			for test in TESTS:
				clientCmd = "netperf -L %s -H %s -t %s -l %s -p 5000" % (localIP, server, test, duration)
				print "start test [%s]: %s" % (test, clientCmd)
				s.check_call(clientCmd, shell=True)
		except s.CalledProcessError:
			self.terminate_server()
			return False

		self.terminate_server()
		return True

	def test_netperf(self):
		self.assertTrue(self.netperf())

if __name__ == "__main__":
	unittest.main()
