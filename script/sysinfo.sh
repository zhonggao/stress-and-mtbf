# !/bin/sh
# Copyright (C) 2014 Intel Corporation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# Author: ethan.gao@intel.com
# Description: collect common system information

echo ""
echo "------------- HOSTNAME -------------------"
echo ""
hostnamectl status
echo ""
echo "------------- /PROC/VERSION --------------"
echo ""
cat /proc/version
echo ""
echo "------------- /PROC/CPUINFO --------------"
echo ""
cat /proc/cpuinfo
echo ""
echo "------------- /PROC/MEMINFO --------------"
echo ""
cat /proc/meminfo
echo ""
echo "------------- /PROC/DEVICES --------------"
echo ""
cat /proc/devices
echo ""
echo "------------- /PROC/INTERRUPTS -----------"
echo ""
cat /proc/interrupts
echo ""
echo "------------- /PROC/IOMEM ----------------"
echo ""
cat /proc/iomem
echo ""
echo "------------- /PROC/PARTITIONS -----------"
echo ""
cat /proc/partitions
echo ""
echo "------------- DF -H ----------------------"
echo ""
df -h
echo ""
echo "------------- LSPCI ----------------------"
echo ""
lspci -kv
echo ""
echo "------------- LSMOD ----------------------"
echo ""
lsmod
echo ""
echo "------------- NW CONFIG -------------------"
echo ""
ip addr show
echo ""
echo "------------- PS -E ----------------------"
echo ""
ps -e
