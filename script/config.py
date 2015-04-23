# !/usr/bin/python
#
# Copyright (C) 2014 Intel Corporation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# Author: ethan.gao@intel.com
# Date:   Aug 29, 2014
# Description:
# Parse general and testcase configuration to start test.
#

import os
import sys
import re
import subprocess
import utils as u
import xml.etree.ElementTree as ET

''' moudle to configure and parse settings '''

CONFIG_FILE = os.getenv("CLRCONFIG")

def parseConfig():
	''' parse config file and return element tree '''
	try:
		etree = ET.parse(CONFIG_FILE)
	except IOError:
		u.logger.critical("Fatal: No configuration file found !")

	if etree.getroot().attrib.get('desc') == 'clr stability':
		return etree
	else:
		u.logger.error('wrong configuration file')
		return None

def generalConfig(subelements=False):
	''' parse general configuration within a dict or an element '''
	tmplist = []
	et = parseConfig()
	g_element = et.find('general')
	if g_element is None:
		u.logger.error('no general configuration is found')
		return None
	if subelements:
		for e in list(g_element):
			tmptuple=(e.tag,e.text)
			tmplist.append(tmptuple)
		return dict(tmplist)
	else:
		return g_element

def updateGenConf(tag, value, newelmt = False):
	''' update value of sub-element underneath gerneral '''
	
	curEtree = parseConfig()
	gen = curEtree.find('general')

	if newelmt:
		newElement = ET.Element(tag)
		gen.append(newElement)

	gen.find(tag).text = str(value)
	curEtree.write(CONFIG_FILE)

def topDir():
	return generalConfig().find('topdir').text

def caseDir(testcase):
	return topDir() + '/' + testcase  

def logDir(testname):
	return caseDir(testname) + '/log'

def srcDir(testname):
	return caseDir(testname) + '/srcpkg'

def binDir():
	return topDir() + '/' + 'bin'

def pkgsDir():
	return topDir() + '/' + 'pkgs'

def NWProxy():
	return generalConfig().find('proxy').text

def testRunner():
	return topDir() + '/' + generalConfig().find('testrunner').text

def testcaseAttr(testname, attr):
	''' retrive specific attribution of a testcase '''
	elmtree = parseConfig()

	for testcase in elmtree.find('testsuite').findall('testcase'):
		if testcase.attrib.get('name') == testname:
			u.logger.debug('find testcase %s'% testname)
			if testcase.attrib.has_key(attr):
				return testcase.attrib.get(attr)
			else:
				raise Exception('No attr %s for testcase %s'% (attr,testname))
		else:
			continue
	else:
		raise Exception('No configuration of testcase %s' % testname)


def testcaseSubElmt(testname, subelmt):
	''' retrieve specific sub element and return its value '''

	elmtree = parseConfig()
	tselmt = elmtree.find('testsuite')

	for testcase in tselmt.findall('testcase'):
		if testcase.attrib.get('name') == testname:
			subfound = testcase.find(subelmt)
			if subfound is not None:
				return subfound.text
			else:
				raise Exception('No subelement %s in testcase %s'% (subelmt,testname))
		else:
			continue
	else:
			raise Exception('Testcase %s is not found'% testname)

def modifyTcConf(testname, key, value):
	''' modify the value of attribution of a test case '''

	elmtTree = parseConfig()
	TcTree = elmtTree.find('testsuite').findall('testcase')

	for testcase in TcTree:
		if testcase.attrib.get('name') == testname:
			if testcase.attrib.has_key(key):
				testcase.set(key, value)
			elif testcase.find(key) is not None:
				testcase.find(key).text = str(value)
			else:
				raise Exception("No key - %s in test case %s" % (key, testname))
			
			elmtTree.write(CONFIG_FILE)
			return True
		else:
			continue
	else:
		raise Exception("Not found test case %s" % testname)


def parameter(testname, subelmt , parameter='parameter'):
	elmtree = parseConfig()
	tselmt = elmtree.find('testsuite')
	for testcase in tselmt.findall('testcase'):
		if testcase.attrib.get('name') == testname :
			subfound = testcase.find(parameter).get(subelmt)
			return subfound
			if subfound is not None:
				return subfound
			else:
				raise Exception('No subelement %s in testcase %s'% (subelmt,testname))
		else:
			continue
	else:
		raise Exception('Testcase %s is not found'% testname)

def resourceName(testname):
	resource = testcaseSubElmt(testname, 'resourcePath')
	return resource.split('/')[-1].strip()

def script2run(testname):
	script = testcaseSubElmt(testname, 'cmd')
	return script.split('/')[-1].strip()

def runScript(testname, args = {}):
	''' Run script included in <cmd></cmd> '''

	scriptToUse = script2run(testname)
	#copy_to_casedir = 'find %s -type f -name %s -print0 | xargs -0 -i cp {} %s' % (binDir(), scriptToUse, caseDir(testname))
	#subprocess.check_call(copy_to_casedir, shell=True)
	os.chdir(srcDir(testname))
	
	runcmd = scriptToUse
	if len(args) != 0:
		for arg in args.values():
			runcmd = runcmd + ' %s' % arg
	
	willRun = "sh -c \"%s\"" % runcmd
	u.logger.info("willRun: %s" % willRun)
	#subprocess.check_call(willRun, shell=True)
	os.system(willRun)

def checkImgVer(img):
	''' check the image version is the same one that we need '''
	if img is None:
		return None

	sysVer = subprocess.check_output('cat /etc/ImageVersion', shell=True)
	sysDate = sysVer.split('-')[2].strip()

	imgDate = '.'.join(img.split('/')[-1].split('-')[-1].split('.')[:3]).strip()

	if sysDate != imgDate:
		raise Exception("Error: you should have aligned test resource with current SW release")
		return False
	else:
		return True

def prepareSrc(testname, pkg=None, untar = True):
	''' prepare test stuff from backup or online resource '''

	NEEDPKGS = []
	
	if pkg is not None: NEEDPKGS.append(pkg)
	
	if testcaseAttr(testname, 'localsrc') == 'No':
		onlinePkg = testcaseSubElmt(testname, 'resourcePath')
		if not u.is_url(onlinePkg):
			raise Exception("Unknown source package !")

		pkgName = onlinePkg.split('/')[-1].strip()
		if re.match('clr-generic.x86_64-\d{2,4}.\d{2}.\d{2}.raw.xz', pkgName) is not None:
			if checkImgVer(pkgName):
				NEEDPKGS.append(onlinePkg)
		else:
			NEEDPKGS.append(onlinePkg)

	if len(NEEDPKGS) == 0:
		print "%s - No extra source packages needed." % testname
		return None

	status,pkgsIn = u.RunCommand('ls %s' % pkgsDir()).run()

	for p in NEEDPKGS:
		filename = p.split('/')[-1]

		if testcaseAttr(testname, 'localsrc') == 'Yes' and filename not in pkgsIn and not u.is_url(p):
			os.system('cp -v %s %s'% (p, srcDir(testname)))
			os.system('cp -v %s %s'% (p, pkgsDir()))
		elif filename in pkgsIn:
			os.system('cp -v %s/%s %s'% (pkgsDir(), filename, srcDir(testname)))
		else:
			u.curlObtain(p, NWProxy())
			os.system('cp -v %s %s' % (filename, srcDir(testname)))
			os.system('cp -v %s %s' % (filename, pkgsDir()))
			os.system('rm -rf %s' % filename)
	
		if untar:
			os.chdir(srcDir(testname))
			u.srcExtract(filename, srcDir(testname))

def buildBin(testname, cmdToBuild = None, subdir = None, cmdToInstall = 'default', pkg2build = None):
	''' Build binary if necessary '''

	if pkg2build is not None:
		# To double ensure in the right place
		os.chdir(u.codeIn(srcDir(testname), pkg2build))
	
	Makefile = 'Makefile'
	makefile = 'makefile'
	configure = 'configure'

	if testcaseAttr(testname, 'binary2build') == 'Yes':
		u.require('make')
		# FIXME - CLR doesn't search sub-folders in env PATH
		#installTo = binDir() + '/' + testcaseAttr(testname, 'name')
		installTo = binDir()

		if cmdToBuild is not None:
			MAKE = cmdToBuild
		else:
			MAKE = 'make all'

		if cmdToInstall == 'default' or cmdToInstall == None:
			INSTALL = "make install --eval='DESTDIR=%s'" % installTo
			#u.mkdir(installTo)
		elif cmdToInstall == 'manual':
			INSTALL = None
		else:
			INSTALL = cmdToInstall

		if subdir is not None:
			MAKE = "%s -C %s" % (MAKE,subdir)
			if INSTALL is not None:
				INSTALL = "%s -C %s" % (INSTALL,subdir)

			if subdir[-1] is '/':
				Makefile = subdir + 'Makefile'
				makefile = subdir + 'makefile'
				configure = subdir + 'configure'
			else:
				Makefile = '/'.join([subdir,'Makefile'])
				makefile = '/'.join([subdir,'makefile'])
				configure = '/'.join([subdir, 'configure'])

		# Make sure there is make file before it really starts
		if u.isfile(Makefile) or u.isfile(makefile) or u.isfile(configure):
			os.system(MAKE)

			if INSTALL is not None:
				u.RunCommand(INSTALL).run()
			else:
				u.manualInstall(srcDir(testname), binDir())
				u.manualInstall(subdir, binDir())
		else:
			raise Exception("No necessary Makefile found!")
	else:
		u.logger.warning("%s -- Not necessary to build running binaries."% testname)

def setup(testname):
	''' Initial setup to execute test '''

	# double confirm runtime top dir
	if not os.path.exists(topDir()):	
		u.mkdir(topDir())
		u.mkdir(binDir())
		u.mkdir(pkgsDir())
	
	u.mkdir(caseDir(testname))
	u.mkdir(srcDir(testname))
	u.mkdir(logDir(testname))
	os.chdir(caseDir(testname))

def back2Runner():
	os.chdir(testRunner())
