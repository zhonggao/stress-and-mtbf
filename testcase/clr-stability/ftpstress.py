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
# Description: download and upload data via ftp
#

import utils
import config
import subprocess as s
import unittest
import os

CASENAME = 'ftpstress'
''' case name '''

SRCPKG = None
''' specific source package with path '''

REQUIREDPKGS = {'curl':'executable', 'expect':'package', 'wget':'executable'}

class FTPStress(unittest.TestCase):
	def setUp(self):
		utils.requiredPkgs(package=REQUIREDPKGS)
		config.setup(CASENAME)
		utils.logger.info("TESTCASE =====> %s <===== START" % CASENAME)
	
	def tearDown(self):
		config.back2Runner()
		utils.logger.info("TESTCASE =====> %s <===== END" % CASENAME)

	def ftp_download(self, file_to_download = 'ftp.download'):
		''' downlaod data from FTP server '''

		FTPSERVER = config.testcaseAttr(CASENAME, 'ftpserver')
		download = "wget %s/%s" % (FTPSERVER, file_to_download)

		try:
			s.check_call(download, shell=True)
		except s.CalledProcessError:
			return False

		if os.path.exists(file_to_download):
			dwlSize = int(s.check_output("du -BM %s | awk '{print $1}'" % file_to_download, shell=True).strip()[:-1])
			expectedSize = int(config.testcaseAttr(CASENAME, 'size'))

			if dwlSize/expectedSize == 1 and dwlSize%expectedSize < 10:
				return True
		
		return False

	def ftp_upload(self, file_to_upload = 'ftp.upload'):
		''' upload data to FTP server '''

		FTPSERVER = config.testcaseAttr(CASENAME, 'ftpserver')
		UPLOADTO = FTPSERVER + '/' + 'upload/'
		upload = "curl -T %s %s -v" % (file_to_upload, UPLOADTO)
		size = int(config.testcaseAttr(CASENAME, 'size'))
		USER = config.testcaseAttr(CASENAME, "user")
		PASSCODE = config.testcaseAttr(CASENAME, "passcode")
		SERVER = FTPSERVER.split(":")[1].strip("//").strip()

		try:
			os.system("dd if=/dev/zero of=%s bs=1M count=%s" % (file_to_upload, size))
			os.system("cp %s/%s %s" % (config.binDir(), 'remove.expect', config.caseDir(CASENAME)))
			s.check_call("sh -c 'expect remove.expect %s %s %s'" % (SERVER, USER, PASSCODE), shell=True)
			s.check_call(upload, shell=True)
		except s.CalledProcessError:
			return False

		return True

	def test_ftp_download(self):
		self.assertTrue(self.ftp_download())

	def test_ftp_upload(self):
		self.assertTrue(self.ftp_upload())

if __name__ == "__main__":
	unittest.main()
