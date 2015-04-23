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
# Date: Sept 9, 2014
# Description: build and run netserver in remote server

run_netserver()
{
	NETDEVS=`ip addr show | grep -iw inet | awk '{print $2}' | cut -d "/" -f1`
	for ip_addr in $NETDEVS
  	  do
		if [[ "${ip_addr}" == "127.0.0.1" ]]; then
			continue
		else
			netserver -4 -L $ip_addr -p 5000
			break
		fi
  	  done
}

which netserver
if [ $? -eq 0 ]; then
	running=`ps -ef | grep "netserver \-4*"`
	if [  -z "${running}" ]; then
		run_netserver
	else
		echo "netserver has already been running."
	fi

	exit 0
fi

mkdir -p /tmp/netserver && rm -rf /tmp/netserver/*
find /tmp -type f -name netperf-*.tar.gz -print | tr -d '\n' | xargs -0 -i tar -xzf "{}" -C /tmp/netserver

#src=`sh -c 'ls -d /tmp/netserver/netper-*' | tr -d '\n'`
#cd $src
cd /tmp/netserver/netperf-2.6.0
sh configure

if [ -f Makefile ]; then
	make all
	make install
fi

which netserver
if [ $? -ne 0 ]; then
	echo "Failed to prepare netserver"
	exit 1
else
	run_netserver
fi

