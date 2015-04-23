import os
import sys
import stat
import optparse
import pprint
import subprocess

RESULT = {"PASS":{"Total": 0}, "FAIL":{"Total": 0}, "ERROR":{"Total": 0}, "TIMEOUT":{"Total": 0}}

def options_parser():
	USAGE = """ Usage: python result.py -p|--plan <plan> -d|--directory <folder> """

	optionParser = optparse.OptionParser(usage =  USAGE)

	optionParser.add_option("-p", "--plan", dest="testplan",
							help="test plan made up of test cases")
	optionParser.add_option("-d", "--directory",dest="report_dir",
							help="directory which holds result data of test cases")

	return optionParser

def is_file(file):
	''' Inspect a regular file '''
	if not os.path.exists(file):
		print "Warning: no such file - %s" % file
		return False

	try:
		mode = os.lstat(file)[stat.ST_MODE]
		if stat.S_ISREG(mode):
			return True
		else:
			return False
	except OSError as e:
		print "Error: %s" % str(e)
		return False

def is_dir(folder):
	''' Inspect a folder '''

	if not os.path.exists(folder):
		print "Error: no such folder - %s" % folder
		return False

	try:
		mode = os.lstat(folder)[stat.ST_MODE]
		if stat.S_ISDIR(mode):
			return True
		else:
			return False
	except OSError as e:
		print "Error %s" % str(e)
		return False

def parse_test_plan(plan):
	''' parse test plan to extract test cases '''

	testcase = []
	keywords = []
	if plan is None or not is_file(plan):
		print "Incorrect test plan and try again !"
		sys.exit(1)

	f = open(plan, 'r')
	try:
		for line in f.readlines():
			if line.startswith('testcases.'):
				testcase.append(line)
			else:
				continue
	finally:
		f.close()

	for tc in testcase:
		keywords.append('.'.join(tc.split('=')[0].strip().split('.')[-2:]))

	return keywords

def quantity(status, keywords):
	''' calculate the amount of test cases in specified status '''

	total = 0
	count = 0

	if not is_dir(status):
		print "Internal exception occurred !"
		sys.exit(1)
	elif len(os.listdir(status)) is 0:
		return False
	else:
		pass

	try:
		for key in keywords:
			count = int(subprocess.check_output("find %s -type d -name %s* -print | wc -l" % (status,key), shell=True))
			if count > 0:
				total += count
			else:
				continue

			if status.upper() in RESULT.keys():
				RESULT[status.upper()][key] = count
			else:
				print "Status [%s]: %s = %d" % (status, key, count)

			count = 0

		RESULT[status.upper()]["Total"] = int(total)
	except subprocess.CalledProcessError as e:
		print "Exception: %s" % str(e)
		return False

def main():
	''' main entry '''
	optionsParser = options_parser()

	if len(sys.argv) < 5:
		print "No enough parameters \n"
		optionsParser.print_help()
		sys.exit(1)

	(options,args) = optionsParser.parse_args()
	if len(args) > 0:
		print "Unknown arguments: %s" % ' '.join(args)
		optionsParser.print_help()
		sys.exit(1)

	if is_dir(options.report_dir):
		os.chdir(options.report_dir)
	else:
		print "Unknown report directory and try again !"
		sys.exit(1)

	tc_keywords = parse_test_plan(options.testplan)

	quantity("pass", tc_keywords)
	quantity("fail", tc_keywords)
	quantity("error", tc_keywords)
	quantity("timeout", tc_keywords)
	
	print "Result Summary:\n"
	pprint.pprint(RESULT,width=1)

if __name__ == "__main__":
	main()
