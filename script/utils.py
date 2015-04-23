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
# This file tries to abstract those common operations which may be
# use in the process of writing CLR stability test cases
#

import os
import time
import stat
import shlex
import shutil
import signal
import socket
import urllib2
import pexpect
import urlparse
import logging
import threading
import traceback
import subprocess
import logging.handlers

'''
module to assist in running system commands and scripts
'''

FILE_LOG_LEVEL="DEBUG"
'''File Level'''

CONSOLE_LOG_LEVEL="INFO"
'''Console Level'''

LOCAL_TIME_STAMP_FORMAT = '%Y-%m-%d_%H:%M:%S'
'''local time format'''

REPORT_TIME_STAMP_FORMAT = '%Y-%m-%d %H:%M:%S'
'''report time format'''

LEVELS={"CRITICAL" :50,
        "ERROR" : 40,
        "WARNING" : 30,
        "INFO" : 20,
        "DEBUG" : 10,
        "NOTSET" :0,
       }
'''logger levels'''

def is_url(path):
	''' Return true if path looks like a URL '''

	url_parts = ()
	# for now, just handle http and ftp
	url_parts = urlparse.urlparse(path)
	return (url_parts[0] in ('http', 'https', 'ftp', 'git'))

def urlopen(url, data=None, timeout=5):
	''' Wrapper to urllib2.urlopen with timeout addition. '''

	# Save old timeout
	old_timeout = socket.getdefaulttimeout()
	socket.setdefaulttimeout(timeout)
	try:
		return urllib2.urlopen(url, data=data)
	finally:
		socket.setdefaulttimeout(old_timeout)

def urlretrieve(url, filename, data=None, timeout=300):
	''' Retrieve a file from given url. '''

	logger.info('Fetching %s -> %s'% (url, filename))
	src_file = urlopen(url, data=data, timeout=timeout)
	try:
		dest_file = open(filename, 'wb')
		try:
			shutil.copyfileobj(src_file, dest_file)
		finally:
			dest_file.close()
	finally:
		src_file.close()

def curlObtain(path,proxy = None):
	''' try to obtain source via utility curl '''

	requiredPkgs(package={'curl':'package'})
	download = None

	if is_url(path) and proxy is not None:
		download = 'curl -O %s -x %s -v'% (path,proxy)
	elif is_url(path):
		download = 'curl -O %s -v'% path
	else:
		logger.error('%s is a wrong url'% path)

	if download is not None:
		os.system(download)


def isfile(file):
	''' Inspect a regular file '''
	if not os.path.exists(file):
		logger.warning("Warning: no such file - %s" % file)
		return False

	try:
		mode = os.lstat(file)[stat.ST_MODE]
		if stat.S_ISREG(mode):
			return True
		else:
			return False
	except OSError as e:
		logger.error("Error: %s" % str(e))
		return False

def isDir(folder):
	''' Inspect a folder '''
	
	if not os.path.exists(folder):
		logger.error("Error: no such folder - %s" % folder)

	try:
		mode = os.lstat(folder)[stat.ST_MODE]
		if stat.S_ISDIR(mode):
			return True
		else:
			return False
	except OSError as e:
		logger.error("Error %s" % str(e))
		return False

def isSymLnk(file):
	''' Inspect a symbolic link '''
	if not os.path.exists(file):
		logger.warning("Warning: No such file - %s" % file)
		return False
	try:
		mode = os.lstat(file)[stat.ST_MODE]
		if stat.S_ISLNK(mode):
			return True
		else:
			return False
	except OSError as e:
		logger.error("Error: %s" % str(e))
		return False

def write2file(filename, data):
	''' write data to a file '''
	
	fd = open(filename, 'wb')
	try:
		fd.write(data)
		fd.flush()
	finally:
		fd.close()

def path_to_sudo():
	s,o = RunCommand('which sudo').run()
	return o.strip()

def wrap_in_sudo(cmd, path_to_sudo, msg = ""):
	''' Wraps a cmd in a sudo call; unless running as root(0,0) '''

	logger.info("\n %s" % msg)
	if  os.getgid() == 0 and os.getuid() == 0:
		return cmd

	return '%s -E sh -c "%s"' % (path_to_sudo, cmd)

def interactRun(cmd, pcode, info, postInfo = None):
	''' Run cmd for the case that interaction is necessary '''

	inst = pexpect.spawn(cmd)
	key = inst.expect([info, pexpect.EOF, pexpect.TIMEOUT])
	if key == 0:
		logger.debug("Found what's expected.")
	elif key == 1:
		logger.debug("Pexpect: Meet EOF.")
	elif key == 2:
		logger.debug("Pexpect: Timeout !")
	else:
		raise Exception("Pexpect: Nothing matches..")

	inst.sendline('%s\r\n'% pcode)
	inst.wait()

def run_with_privilege(cmd,pcode,msg = None):
	''' Run cmd with super user privilege '''

	ret,who = RunCommand('whoami').run()

	default = '\[sudo\] password for %s: '% who.strip()
	cmd = wrap_in_sudo(cmd, path_to_sudo())

	if msg is None:
		expectInfo = default
	else:
		expectInfo = msg

	interactRun(cmd, pcode, expectInfo)

def pkgType(pkg):
	''' parse package type '''

	if pkg is None:
		return None
	
	fmt = None
	ext = pkg.split('.')[-1].lower()
	if pkg.split('.')[-2].lower() != 'tar':
		fmt = ext
	else:
		if ext == 'bzip2':
			fmt = 'tar.bzip2'
		elif ext == 'xz':
			fmt = 'tar.xz'
		elif ext == 'gz':
			fmt = 'tar.gz'
		else:
			raise Exception('Unknow package type')

	return fmt

def sysinfo(tofile='sysinfo.log'):
	''' collect system information '''

	ret,sinfo = RunCommand('sh sysinfo.sh').run()
	if ret == 0:
		write2file(tofile, sinfo)

def require(exe):
	''' Tell whether 'exe' is installed on the machine '''

	Installed = False
	try:
		cmd = 'which %s'% exe
		RunCommand(cmd).run()
		Installed = True
	except:
		tryToInstall = "zypper -n install --type package %s" % exe
		RunCommand(tryToInstall).run()
		Installed = True

	return Installed

def codeIn(dest,pkgname):
	''' parse the real folder holding source code
		@param pkgname: a tarball source package
	'''
	pkgname = pkgname.split('/')[-1].strip()
	ext = pkgType(pkgname)
	index = pkgname.rfind(ext)
	if dest is not None:
		path = dest + '/' + pkgname[:(index-1)]
	else:
		path = pkgname[:(index-1)]

	return path

def srcExtract(src,dest):
	''' extract source package from archive format '''
	
	ext = None
	uncompress = None

	if dest is None: dest = os.getcwd()
	if isfile(src) and os.path.exists(dest):
		ext = pkgType(src)
	else:
		raise Exception('failure during extracting source package !')

	if ext == 'tar': uncompress = 'tar -xf %s -C %s'% (src,dest)
	if ext == 'xz': uncompress = 'xz -k -d -T 0 %s' % src
	if ext == 'zip': uncompress = 'unzip %s' % src
	if ext == 'tar.bzip2': uncompress = 'tar -xjf %s -C %s'% (src,dest)
	if ext == 'tar.xz': uncompress = 'tar -xJf %s -C %s'% (src,dest)
	if ext == 'tar.gz': uncompress = 'tar -xzf %s -C %s'% (src,dest)
	
	RunCommand(uncompress, timeout=300).run()

	holder = codeIn(dest,src)
	if isDir(holder):
		os.chdir(holder)

def manualInstall(binFrom, to):
	''' try to install binary to specified place '''

	executable = []
	installed = []

	if os.path.exists(binFrom):
		executable = subprocess.check_output("file %s/* | grep -iw executable | awk '{print $1}'" % binFrom, shell=True).rsplit(':\n')
	else:
		logger.error("%s: No such file or directory" % binFrom)
		return None
	
	if len(executable) == 0:
		return None

	if os.path.exists(to):
		for exe in executable:
			if exe != '': 
				os.system('install -m 0755 %s %s' % (exe, to))
				installed.append(exe)
	else:
		logger.error("%s No such file or directory" % to)
		return None

	return installed


def requiredPkgs(bridge='zypper', package={}):
	''' Check installation status of dependent packages '''

	if len(package) == 0:
		logger.warning("No dependent packages are required !")
		return 0
	
	require(bridge)
	zyppcheck = None
	rpmcheck = None
	pkgstatus = None

	for k,v in package.iteritems():
		if bridge == 'zypper':
			if v == 'package':
				plist = 'zypper packages --installed-only'
			elif v == 'pattern':
				plist = 'zypper patterns --installed-only'
			elif v == 'executable':
				require(k)
				continue
			else:
				logger.warning("type %s isn't implemented. please extend if you indeed need !")

			zyppcheck = "%s | grep -iw '%s' | awk '{print $6}'"% (plist, k)
		elif bridge == 'rpm':
			if v == 'executable':
				require(k)
				continue
			else:
				pinfo = 'rpm -qi %s'% k
				rpmcheck = "%s | grep -io 'Install Date'"% pinfo
		else:
			raise Exception('Unknown bridge %s'% bridge)

		try:
			if (zyppcheck is not None and subprocess.check_output(zyppcheck, shell=True).strip() == k) \
				or (rpmcheck is not None and  subprocess.check_output(rpmcheck, shell=True).strip() == 'Install Date'):
				pkgstatus = 'Installed'
			else:
				pkgstatus = 'Try2Install'
		except subprocess.CalledProcessError:
			pkgstatus = 'Try2Install'
		
		if pkgstatus == 'Installed':
			logger.info('%s -- %s is already installed in system, go ahead...'% (v,k))
		elif pkgstatus == 'Try2Install':
			logger.warning("%s isn't installed and try to install..."% k)
			try2install="zypper -n install --type %s '%s'"% (v,k)
			subprocess.check_call(try2install, shell=True)
		else:
			logger.warning('Unknown package status for %s'% k)

def mkdir(path):
    '''
    create a folder
    @type path: string
    @param path: the path of folder
    @rtype: string
    @return: the path of the folder, return None if fail to create folder
    '''
    if os.path.exists(path):
        shutil.rmtree(path, onerror=forcerm)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def forcerm(fn, path, excinfo):
    '''
    force delete a folder
    @type path: string
    @param path: the path of folder
    @type excinfo: string
    @param excinfo: the output info when exception
    '''
    if fn is os.rmdir:
        os.chmod(path, stat.S_IWRITE)
        os.rmdir(path)
    elif fn is os.remove:
        os.chmod(path, stat.S_IWRITE)
        os.remove(path)

class Command(object):
    """
    Enables to run subprocess commands in a different thread with TIMEOUT option.
    """
    command = None
    process = None
    status = None
    output, error = '', ''
 
    def __init__(self, command):
        if isinstance(command, basestring):
            command = shlex.split(command)
        self.command = command
 
    def run(self, timeout=None, **kwargs):
        """ Run a command then return: (status, output, error). """
        def target(**kwargs):
            try:
                self.process = subprocess.Popen(self.command, **kwargs)
                self.output, self.error = self.process.communicate()
                self.status = self.process.returncode
            except:
                self.error = traceback.format_exc()
                self.status = -1

        # default stdout and stderr
        if 'stdout' not in kwargs:
            kwargs['stdout'] = subprocess.PIPE
        if 'stderr' not in kwargs:
            kwargs['stderr'] = subprocess.PIPE

        # thread
        thread = threading.Thread(target=target, kwargs=kwargs)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            self.kill_proc(self.process.pid)
            thread.join()
        return self.status, self.output, self.error

    def kill_proc(self, pid):
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass

class RunCommand(Command):
    """
    run commands in shell
    """
    def __init__(self, cmd, retry=3, timeout=10):
        Command.__init__(self, cmd)
        self.retry = retry
        self.timeout = timeout

    def run(self):
        output = None
        error = None
        status = -1
        while self.retry:
            status, output, error = Command.run(self, timeout=self.timeout, stderr=subprocess.STDOUT)
            if not status:
                return status, output
            else:
                self.retry -= 1
        if output:
        	raise Exception(str(output))
        elif error:
            raise Exception(str(error))
			
class Logger:
    '''
    class used to print log
    '''
    _instance=None
    _mutex=threading.Lock()

    def __init__(self, level="DEBUG"):
        '''
        constructor of Logger
        '''
        self._logger = logging.getLogger("clrstability")
        self._logger.setLevel(LEVELS[level])
        self._formatter = logging.Formatter("[%(asctime)s] - %(levelname)s : %(message)s",'%Y-%m-%d %H:%M:%S')
        self._formatterc = logging.Formatter("%(message)s")
        self.add_file_logger()
        self.add_console_logger()

    def add_file_logger(self, log_file="./caselog/run.log", file_level="DEBUG"):
        '''
        generate file writer
        @type log_file: string
        @param log_file: the path of log file
        @type file_level: string
        @param file_level: the log output level.Defined in global LEVELS
        '''
        logFolder = 'caselog'
        mkdir(logFolder)
        if not os.path.exists(log_file):
            open(log_file,'w')
            
        fh = logging.handlers.RotatingFileHandler(log_file, mode='a', maxBytes=1024*1024*1,
                                                   backupCount=100,encoding="utf-8")
        fh.setLevel(LEVELS[file_level])
        fh.setFormatter(self._formatter)
        self._logger.addHandler(fh)

    def add_console_logger(self, console_level="INFO"):
        '''
        generate console writer
        @type console_level: string
        @param console_level: the level of console
        '''
        ch = logging.StreamHandler()
        ch.setLevel(LEVELS[console_level])
        ch.setFormatter(self._formatterc)
        self._logger.addHandler(ch)

    @staticmethod
    def getLogger(level="DEBUG"):
        '''
        return the logger instance
        @type level: string
        @param level: the level of logger
        @rtype: Logger
        @return: the instance of Logger      
        '''
        if(Logger._instance==None):
            Logger._mutex.acquire()
            if(Logger._instance==None):
                Logger._instance=Logger(level)
            else:
                pass
            Logger._mutex.release()
        else:
            pass
        return Logger._instance

    def debug(self, msg):
        '''
        print message for debug level
        @type msg: string
        @param msg: the content of msg      
        '''
        if msg is not None:
            self._logger.debug(msg)

    def info(self, msg):
        '''
        print message for info level
        @type msg: string
        @param msg: the content of msg      
        '''
        if msg is not None:
            self._logger.info(msg)

    def warning(self, msg):
        '''
        print message for warning level
        @type msg: string
        @param msg: the content of msg      
        '''
        if msg is not None:
            self._logger.warning(msg)

    def error(self, msg):
        '''
        print message for error level
        @type msg: string
        @param msg: the content of msg      
        '''
        if msg is not None:
            self._logger.error(msg)

    def critical(self, msg):
        '''
        print message for critical level
        @type msg: string
        @param msg: the content of msg      
        '''
        if msg is not None:
            self._logger.critical(msg)

logger = Logger.getLogger()
'''single instance of logger'''
