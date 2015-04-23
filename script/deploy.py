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
# Date:   Sept 9, 2014
# Description: Automate deployment process of stability test

import os
import sys
import optparse
try:
	import config
	import utils
except ImportError:
	print "ImportError occurred with module config and utils"
	sys.exit()
	
def config_option_parser():
	DESCRIPTION = """
	Stability Evaluation - Clear Linux OS for Intel Architecture.
	Usage: deploy.py --plan <test plan> --cycle <num> --release <SW version> --deviceID <serial number> --report
	"""
	optionParser = optparse.OptionParser(usage = DESCRIPTION)

	optionParser.add_option('-l', '--srcfrom', 
							dest='local_src_top',
							help='top dir of local copy for stability test resource in repository')
	optionParser.add_option('-r', '--runtime',
							dest='runtime_top', default='/opt/stability',
							help='top dir for runtime ')
	optionParser.add_option('--proxy', dest='proxy',default=None,
							help='network proxy to assist in accessing data from Internet')
	optionParser.add_option('--release', dest='version',default='20140101',
							help='SW release that test will base on')
	optionParser.add_option('--deviceid', dest='devid', 
							type='string', default='D54250WYK',
							help='device serial number of DUT')
	optionParser.add_option('--plan', dest='customPlan', default=None,
							help='run custom test plan')
	optionParser.add_option('--duration', dest='duration', default='07D00H00M00S',
							help='duration to keep running test')
	optionParser.add_option('--cycle', dest='times', default=None,
							help='how many times to repeat running testcases')
	optionParser.add_option('--livereport', dest='report',
							action='store_true', default=False,
							help='enable or disable live report test result')
	optionParser.add_option('--dryrun', dest='dryrun',
							action='store_true', default=False,
							help='double check the necessary to really start')
	
	return optionParser

def repoShadow(username, password, repo):
	''' Shadow test resource repository to local path '''

	prompt = "Password for 'https://%s@git-ccr-1.devtools.intel.com': "% username
	if not utils.require('git'):
		os.system('zypper -n install --type package git')

	e = repo.split('//')
	if len(e) != 2:
		utils.logger.error('Error occured while shadow repos')
	else:
		usrRepo = e[0] + '//' + username + '@' + e[1]

	cloneRepo = 'git clone %s'% usrRepo

	utils.interactRun(cloneRepo, password, prompt)

def reportServer():
	''' Setup server to report and depict test result '''
	pass

def noseRunner(srctop, proxy):
	''' prepare test runner to run test cases '''
	
	if not utils.require('pip'):
		os.system('python get-pip.py --proxy=%s' % proxy)
	
	os.system('pip install nose --proxy=%s' % proxy)
	os.system('pip install requests --proxy=%s' % proxy)

	runnerPkg = srctop + '/' + 'framework/' + 'noserunner.tar.gz'
	utils.srcExtract(runnerPkg, config.topDir())

	if utils.isfile('runtests.py'):
		utils.logger.info("test runner is already ready...")
	
	os.system('python runtests.py -h')

def configClient(release, deviceid):
	''' config client.config and server.config '''
	
	if utils.isfile('client.config'):
		os.system("sed -i '/revision/crevision = %s' client.config"% release)
		os.system("sed -i '/deviceid/cdeviceid = %s' client.config"% deviceid)

def configServer():
	pass

def prepareNmon(srcpkg = 'nmon_x86_64_clr.tar.xz'):
	''' prepare system monitor to use '''

	srctar = config.pkgsDir() + '/' + srcpkg

	deps = {'ncurses-dev':'package', 'make':'package'}
	utils.requiredPkgs(package=deps)

	utils.srcExtract(srctar,config.topDir())
	utils.RunCommand('make nmon_x86_64_clr').run()
	utils.RunCommand("make install --eval='DESTDIR=%s'" % config.binDir()).run()

def prepareTCs(srctop):
	''' prepare stability test case to run '''

	if not os.path.exists(config.testRunner()):
		raise Exception("test runner is not ready, please prepare it first.")

	tcPkg = srctop + '/' + 'testcase/' + 'clr-stability.tar.gz'
	tchome = config.testRunner()  + '/testcases'
	utils.srcExtract(tcPkg, tchome)

	if utils.isfile('kernelbuild.py'):
		utils.logger.info("test cases are ready in %s" % os.getcwd())

def kickOff(srctop, option = {}):
	''' Start to run test cases '''

	mtbf_plan = None
	non_mtbf_plan = None

	if option.customPlan is None:
		mtbf_plan = srctop + '/' + 'testcase/' + 'clr-stability-mtbf-plan'
		non_mtbf_plan = srctop + '/' + 'testcase/' + 'clr-stability-non-mtbf'
	else:
		if "non-mtbf" in option.customPlan:
			non_mtbf_plan = option.customPlan
		else:
			mtbf_plan = option.customPlan

	if option.times is None:
		cycle2test = ''
	else:
		cycle2test = '--cycle %s'% option.times

	if option.report:
		resultReport = '--livereport'
	else: 
		resultReport = ''

	if option.duration is not None and option.times > 0:
		duration2run = ''
	else:
		duration2run = '--duration %s'% option.duration

	if mtbf_plan is not None:
		os.system('cp -v %s %s' % (mtbf_plan, config.testRunner()))
		mtbf_test = 'python runtests.py --plan-file %s %s %s %s --timeout 7200' % (mtbf_plan.split('/')[-1].strip(), duration2run, cycle2test, resultReport)
	
	if non_mtbf_plan is not None:
		os.system('cp -v %s %s' % (non_mtbf_plan, config.testRunner()))
		non_mtbf_test = 'python runtests.py --plan-file %s --cycle 1 %s --timeout 7200' % (non_mtbf_plan.split('/')[-1].strip(), resultReport)

	os.chdir(config.testRunner())
	
	if option.dryrun:
		# reaching here means no prior exceptions 
		print "MTBF test in DUT - %s: %s "% (option.devid, mtbf_test)
		print "Non MTBF test in DUT - %s: %s"% (option.devid, non_mtbf_test)
		# check noserunner availability
		os.system('python runtests.py -h')
		# check existence of test plan
		utils.isfile('clr-stability-mtbf-plan')
		# check runnability of system monitor
		utils.sysinfo()
		utils.RunCommand('nmon_x86_64_clr -h').run()
		print "it seems like everything is in place, you're recommended continuing to real run..."
	else:
		utils.sysinfo('sysinfo.start')
		os.system('nmon_x86_64_clr -f -s 360 -c 2400')
		os.system(mtbf_test)
		os.system(non_mtbf_test)
		utils.sysinfo('sysinfo.end')

def updateConf(option = {}):
	''' update runtime or test cases' configuration '''
	
	conf_need_change = {'vmloop': {'resourcePath': {'value': None, 'prompt': "Did you update the url to download raw image, yes/no?", 'yes': "Reminder: Don't use local mirror but download.clearlinux.org", 'no': "please specify the url to download raw image from download.clearlinux.org:"}},
						'exercise_container': {'repo': {'value': None, 'prompt': "Did you update the url of the repository, yes/no?", 'yes': "Reminder: Make sure your repository works", 'no': "please specify the url of repository:"}}}

	# Do update for environmental settings at runtime
	config.updateGenConf('topdir', option.runtime_top)
	config.updateGenConf('proxy', option.proxy)

	# Do modificatin of test cases' configuration if necessary
	print """
		###########################################################
		# In order to make sure the correct settings of certain   #
		# test cases have already been finished in the overall    #
		# configuration file for each release before stability    #
		# test starts, please reply <yes or no> for the following #
		# confirmation to set or stop to manually update and then #
		# try again!                                              #
		##########################################################
		"""
	for test in conf_need_change.keys():
		for conf in conf_need_change[test].keys():
			ANSWER = raw_input("[%s] - %s" % (test, conf_need_change[test][conf].get('prompt')))
			if ANSWER.lower() == "yes":
				print "%s" % conf_need_change[test][conf].get('yes')
			elif ANSWER.lower() == "no":
				ANSWER = raw_input("[%s] - %s" % (test, conf_need_change[test][conf].get('no')))
				conf_need_change[test][conf]['value'] = ANSWER.strip()
				config.modifyTcConf(test,conf,conf_need_change[test][conf].get('value'))
			else:
				print "Unkonwn answer and stop here !"
				sys.exit()

			try:
				print "Current settings [%s -> %s]: %s" % (test,conf,config.testcaseAttr(test, conf))
			except:
				print "Current settings [%s -> %s]: %s" % (test,conf,config.testcaseSubElmt(test, conf))

def main():
	''' Main entry to real start '''	

	optionParse = config_option_parser()

	if len(sys.argv) < 5:
		utils.logger.error("No enough parameters\n")
		optionParse.print_help()
		sys.exit()

	(options, args) = optionParse.parse_args()
	if len(args) > 0:
		utils.logger.error("Unknown CLI arguments: %s"% ' '.join(args))
		optionParse.print_help()
		sys.exit()

	# prepare runtime environment
	utils.logger.info('top dir of local test source resides at: %s'% options.local_src_top)

	os.chdir(options.local_src_top)

	tcconfig = options.local_src_top + '/clrconfig.xml'	
	os.system('cp -v %s %s' % (tcconfig, options.runtime_top))

	#config.updateGenConf('topdir', options.runtime_top)
	#config.updateGenConf('proxy', options.proxy)
	updateConf(options)

	pkgsFrom = options.local_src_top + '/package/*'
	utils.mkdir(config.pkgsDir())
	os.system('cp -v %s %s' % (pkgsFrom, config.pkgsDir()))

	scripts = options.local_src_top + '/script/*'
	utils.mkdir(config.binDir())
	os.system('cp -v %s %s' % (scripts, config.binDir()))

	# setup report server
	reportServer()

	# prepare test runner
	noseRunner(options.local_src_top, options.proxy)
	configClient(options.version, options.devid)
	configServer()

	prepareNmon()

	# prepare test case
	prepareTCs(options.local_src_top)

	# start to run and collect system info at the begin and end
	kickOff(options.local_src_top, options)


if __name__ == "__main__":
	main()
