# -*- coding: utf-8 -*-
#================================================
import sys
#sys.path.append("/var/lib/python-support/python2.5/")
#sys.path.append("/var/lib/python-support/python2.6/")
#sys.path.append("/usr/share/pyshared/")
#sys.path.append("/usr/lib/pymodules/python2.6/")
import sys
import os
import atexit
import getopt
import json
import threading
import signal, os,time,re
import imp
import shutil

import nvwa.pcolor
import nvwa.pprint
"""
"""

__author__ = "xurenlu"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2008 xurenlu"
__license__ = "LGPL"

def sig_exit():
    """ handle the exit signal
    """
    print "[end time]:"+str(time.time())
    print nvwa.pcolor.pcolorstr("CAUGHT SIG_EXIT signal,exiting...",nvwa.pcolor.PHIGHLIGHT,nvwa.pcolor.PRED,nvwa.pcolor.PBLACK)
    global config
    try:
        os.remove(config["pid"])
    except:
        pass
    sys.exit()

def handler(signum, frame):
    """
    handle signals
    """
    sig_exit()
    if signum == 3:
        sig_exit()
    if signum == 2:
        sig_exit()
    if signum == 9:
        sig_exit()
        return None

def prepare_taskfile(taskfile):
    """Attempt to load the taskfile as a module.
    """
    path = os.path.dirname(taskfile)
    taskmodulename = os.path.splitext(os.path.basename(taskfile))[0]
    fp, pathname, description = imp.find_module(taskmodulename, [path])
    #print "fp:",fp,",pathname:",pathname,",desc:",description
    try:
        return imp.load_module(taskmodulename, fp, pathname, description)
    finally:
        if fp:
            fp.close()

def inittask(task,type="web"):
    """init a task and create empty files for you 
    """
    try:
        os.mkdir(task,0755)
    except Exception,e:
        print "exception:",e
        pass
    try:
        shutil.copyfile("share/templates/project-%s.py" % type,"%s/%s.py" % (task,task) )
    except Exception,e:
        print "exception:",e
        pass
    try:
        shutil.copyfile("share/templates/config-%s.py" % type,"%s/config.py" % task )
    except:
        pass

def handle_pid(pidfile):
    """
    handle pid files
    """
    pid=os.getpid()
    try:
        lastpid=int(open(pidfile).read())
    except:
        lastpid=0
        pass
    try:
        if lastpid>0:
            os.kill(lastpid,3)
    except:
        pass
    fp=open(pidfile,"w")
    fp.write(str(pid))
    fp.close()

def at_exit():
    """
    hook of exit
    """
    end_time=time.time()
    print "[end time]:"+str(end_time)
    print "[cost time]:"+str(end_time-start_time)
    print "\n=========================\n"

def usage():
    print "usage:\t",sys.argv[0],' [start|startdaemon] taskfile' 
    print "usage:\t",sys.argv[0],' stop taskfile' 
    print "usage:\t",sys.argv[0],' help' 


def handle_log(logfile,callback):
    pw,pr = os.popen2("tail -f %s" % logfile,"rw");
    while 1:
        l = pr.readline()
        callback(l) 

def stop_process(pidfile):
    try:
        lastpid=int(open(pidfile).read())
    except:
        lastpid=0
        pass
    try:
        if lastpid>0:
            os.kill(lastpid,3)
    except:
        print "exit failed."
    
def daemonize():
    '''
    This forks the current process into a daemon.
    '''
    # flush io
    sys.stdout.flush()
    sys.stderr.flush()
    # Do first fork.
    try:
        pid = os.fork()
        if pid > 0: sys.exit(0) # Exit first parent.
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)       
    # Decouple from parent environment.
    os.chdir("/")
    os.umask(0)
    os.setsid()
    # Do second fork.
    try:
        pid = os.fork()
        if pid > 0: sys.exit(0) # Exit second parent.
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(1)

def handle_signals():
    signal.signal(signal.SIGINT,handler)
    signal.signal(signal.SIGTERM,handler)
    signal.signal(3,handler)

    #如果子进程退出时主进程不需要处理资源回收等问题
    #这样可以避免僵尸进程
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)

    sys.getdefaultencoding()
    reload(sys)
    sys.setdefaultencoding("utf-8")
    start_time=time.time()

