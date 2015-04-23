# !/bin/sh
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
# Description: Automate stability test procedure
#

NO_ARGS=0
E_OPTERR=-1

RUNTIME="/opt/stability"
SRCTMP="/tmp/stability"
CONFNAME="clrconfig.xml"

RUN_CYCLE=0
RUN_DURATION="10D00H00M00S"
LIVEREPORT=""

usage(){

	echo -e "\nUsage: `basename $0` [options]..."
	echo "options:"
	echo "  -h, --help: show help information"
	echo "  -s,--repo: online repository which places test resource"
	echo "  -a,--proxy: proxy to facilitate network access"
	echo "  -u,--user: user name of account to access repository"
	echo "  -r,--release: software release"
	echo "  -d,--dut: serial number of DUT"
	echo "  -c,--cycle: test cycles to run"
	echo "  -t,--duration: duration to keep running test, it defauls to 24 x 10 hours"
	echo "  -l,--livereport: enable or disable report live test results, it's disabled by default"
	echo "  --runtime: where to conduct all tests"
	echo "  --srccopy: where to place local copy of test source"
	echo "  --dryrun: dry run to simply inspect that the preliminary stuff is ready."
}

inputOptions=`getopt -o s:a:u:p:r:d:hc:t:l -l repo:,proxy:,user:,passwd:,release:,dut:,help,cycle:,duration:,livereport,runtime:,srccopy:,dryrun -- "${@}"`

if [[ ($? -ne 0) || ($# -eq $NO_ARGS) ]]; then
	echo "Terminating..." >&2  
	usage
	exit $E_OPTERR
fi

eval set -- "${inputOptions}"

while true; do
	case "$1" in
		-s|--repo) REPO="$2"; shift 2 ;;
		-a|--proxy) PROXY="$2"; shift 2 ;;
		-u|--user) USER="$2"; shift 2 ;;
		-p|--passwd) PASSWD="$2"; shift 2 ;;
		-r|--release) RELEASE="$2"; shift 2 ;;
		-d|--dut) SERIALNO="$2"; shift 2 ;;
		-h|--help) usage; exit 0; shift ;;
		-c|--cycle) RUN_CYCLE="$2"; shift 2 ;;
		-t|--duration)
		  case "$2" in
			"") 
			  echo "Default to run for 7 days."
			  shift 2
			  ;;
			*)
			  RUN_DURATION="$2"
			  shift 2
			  ;;
		  esac ;;
		-l|--livereport) LIVEREPORT="yes"; shift ;;
		--runtime) RUNTIME=$2; shift 2 ;;
		--srccopy) SRCTMP=$2; shift 2 ;;
		--dryrun) DRYRUN="yes"; shift ;;
		--) 
		  shift
		  break
		  ;;
		*)
		  echo "Internal error !"
		  usage
		  exit $E_OPTERR
		  ;;	
	esac
done

read -p "Have you rebooted DUT before real stability test starts(yes/no/reboot)? " ANSWER
ANSWER=`echo $ANSWER | tr [:lower:] [:upper:]`
if [[ "${ANSWER}" == "YES" ]]; then
        echo "Continue ..."
elif [[ "${ANSWER}" == "REBOOT" ]]; then
        echo "WARNING: DUT will be rebooted in 60 seconds and please save everything well"
        shutdown -r +1
        exit 0
elif [[ "${ANSWER}" == "NO" ]]; then
        echo "DUT should have been rebooted for a clear test environment"
        exit 0
else
        echo "Error: Unknown selection. exit ..."
        exit 1
fi

if test -n "${PASSWD}" ; then
	echo "WARN: PASSWORD IN THE FORMAT OF PLAIN TEXT IS FORBIDDEN HERE !"
	PASSWD=""
fi

zypper -n install --type pattern "Development Tools"

# check existence for git and pip 
which git >& /dev/null && which pip >&/dev/null
if [[ $? != 0 ]]; then
	zypper -n install --type package git
	python get-pip.py --proxy=$PROXY
fi

pip install pexpect --proxy=$PROXY

# set up environmental settings (please don't change if you're unsure)
export CLRCONFIG="${RUNTIME}/${CONFNAME}"

found=`(cat /etc/profile | grep -iw ${RUNTIME}) || (echo $PATH | grep -io ${RUNTIME})`
if [[ -z $found ]]; then
	echo "Append environmental PATH for runtime purpose"
	sed -i "\$a export PATH=\$PATH:$RUNTIME/bin" /etc/profile
fi

source /etc/profile
echo "current environmental PATH is: $PATH"

# prepare local copy of test resource 
if [[ ${PASSWD} == "" ]]; then
	python shadow.py --username $USER --repository $REPO --agent $PROXY --local $SRCTMP
else
	python shadow.py --username $USER --password $PASSWD --repository $REPO --agent $PROXY --local $SRCTMP
fi

# start to deploy and test
LOCAL_SRC_TOP=$SRCTMP
LOCAL_SRC_TOP=`find $LOCAL_SRC_TOP -type f -name $CONFNAME -print | xargs -0 -i dirname "{}"`

echo "Interim test resource resides at: $LOCAL_SRC_TOP"
rm -rf $RUNTIME && mkdir -p $RUNTIME
sh -c "cp $LOCAL_SRC_TOP/script/*.py $RUNTIME" && cd $RUNTIME

runcmd="python deploy.py --srcfrom $LOCAL_SRC_TOP --runtime $RUNTIME --proxy $PROXY --release $RELEASE --deviceid $SERIALNO"
if [ $RUN_CYCLE -gt 0 ]; then
	runcmd=$runcmd" --cycle $RUN_CYCLE"
elif [ -n $RUN_DURATION ]; then
	runcmd=$runcmd" --duration $RUN_DURATION"
fi

if [[ $LIVEREPORT == "yes" ]]; then
	runcmd=$runcmd" --livereport"
fi

if [[ $DRYRUN == "yes" ]]; then
	runcmd=$runcmd" --dryrun"
fi

echo "Start...: $runcmd"
sh -c "$runcmd"
