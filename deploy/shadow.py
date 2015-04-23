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
# Date: Sept 11, 2014
# Description: Start to prepare initial resource

import os
import sys
import pexpect
import optparse
import subprocess

def options_parser():
	USAGE = """ Usage: shadow.py -u <user> -p <password> -r <repo> -a <agent> -l <local> """

	optionParser = optparse.OptionParser(usage =  USAGE)

	optionParser.add_option("-u", "--username",
							dest="user", type="string",
							help="user name to access online repository")
	optionParser.add_option("-p", "--password",
							dest="passwd", type="string", default="",
							help="password of user")
	optionParser.add_option("-r", "--repository", dest="repo",
							help="online repository where places test resource")
	optionParser.add_option("-a", "--agent", dest="proxy",
							help="network agent to facilitate network access")
	optionParser.add_option("-l", "--local", dest="localsrc", default="/tmp/stability",
							help="local path to hold test resoure")	

	return optionParser

def shadowRepo(user, passcode, repo):
	''' Shadow online resource to the local '''
	
	parts = repo.split('//')
	
	if len(parts) == 2:
		usr_repo = parts[0] + '//' + user + '@' + parts[1]
		prompt = "Password for '%s//%s@%s': " % (parts[0], user, parts[1].split('/')[0])
		print "expected prompt is: %s" % prompt
	else:
		raise Exception("error occured while to shadow repository !")

	shadow_repo = "git clone %s" % usr_repo

	if len(passcode) == 0:
		subprocess.check_call(shadow_repo, shell=True)
		return 0
	else:
		print "WARNING: there may be security risk in this way!"

	child = pexpect.spawn(shadow_repo)
	key = child.expect([prompt, pexpect.EOF, pexpect.TIMEOUT])
	if key == 0: 
		print "Pexpect: Found."
	elif key == 1:
		print "Pexpect: EOF."
	elif key == 2:
		print "Pexpect: Timeout."
	else:
		raise Exception("Pexpect: Failed to match anything...")

	child.sendline("%s\r\n" % passcode)
	child.wait()

def main():
	''' main entry '''

	optionsParser = options_parser()

	if len(sys.argv) < 7:
		print "No enough parameters \n"
		optionsParser.print_help()
		sys.exit()

	(options,args) = optionsParser.parse_args()
	if len(args) > 0:
		print "Unknown arguments: %s" % ' '.join(args)
		optionsParser.print_help()
		sys.exit()

	os.system("mkdir -p %s" % options.localsrc)
	os.chdir(options.localsrc)
	os.system("rm -rf *")

	shadowRepo(options.user, options.passwd, options.repo)
	
if __name__ == "__main__":
	main()	
