# -*- coding: utf-8 -*-
# vim: set fdm=expr:
"""
fccpm is "files,crontabs,configurations,processes manager"
"""
__author__ = "xurenlu"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2008 xurenlu"
__license__ = "LGPL"

import os
import sys
#sys.path.append(os.path.realpath(os.path.dirname(__file__)))
import atexit
import getopt
import threading
import signal, os,time,re
import imp
import shutil
import sqlite3 as sqlite
import simplejson as pickle
import nvwa.pcolor as pcolor
import nvwa.log as log


#PREFIX=os.path.dirname(os.path.dirname(os.path.realpath(__file__)))+"/"
PREFIX="/home/x/"
SUPERVISOR_CONF_DIR="/etc/supervisor/"
VERSION = "1.0.0"

def prepare_taskfile(taskfile):
    """Attempt to load the taskfile as a module.
    """
    path = os.path.dirname(taskfile)
    taskmodulename = os.path.splitext(os.path.basename(taskfile))[0]
    try:
        fp, pathname, description = imp.find_module(taskmodulename, [path])
        tmp = imp.load_module(taskmodulename, fp, pathname, description)
        fp.close()
        return tmp
    except Exception,e:
        log.error("got an error :"+str(e))
        pass

def _get_db():
    '''get the connection of the db'''
    cx=sqlite.connect(PREFIX + "db/packages.db")
    return cx

def _package_config(package,version):
    '''prepare the package config file,read the configuration'''
    metafile = PREFIX+"/packages/"+package+"/"+version+"/"+package+"-"+version+".py"
    try:
        k=prepare_taskfile(metafile)
    except Exception,e:
        pass
    return k
	
def init_db():
    '''initialize the fccpm db file'''
    dir_name = PREFIX + "db/"
    if not os.path.isdir(dir_name):
        try:
            os.makedirs(dir_name)
        except:
            print "mkdir "+ dir_name +" failed"
            pass
    cx = _get_db()
    cu = cx.cursor()
    create_sql = """
    create table  packages (package varchar(32),version varchar(16),status varchar(16), cron_status varchar(3))
    """
    cu.execute(create_sql)
    cu.execute("insert into packages values ('fccpm','"+VERSION+"','normal','on')")
    cx.commit()

def list_packges(package_name=''):
    ''' list the package installed in the system'''
    cx = _get_db()
    cu = cx.cursor()
    if package_name == "":
        cu.execute("select package,version,status,cron_status from packages ")
    else:
        cu.execute("select package,version,status,cron_status from packages where package like '%" + package_name+ "%'")

    rows = cu.fetchall()
    return rows

def get_current_version(package_name):
    ''' list the package installed in the system'''
    cx = _get_db()
    cu = cx.cursor()
    cu.execute("select package,version,status from packages where package = '" + package_name+ "' and status='normal'") 
    rows = cu.fetchone()
    return rows


def list_files(package,version):
    """List all files and dirs of package"""
    metafile = PREFIX+"/packages/"+package+"/"+version+"/"+package+"-"+version+".py"
    k=prepare_taskfile(metafile)
    f_file =open( PREFIX+"/packages/"+package+"/"+version+"/"+package+"-"+version+"/"+ package+"-"+version+".files.dat","r")
    d_file = open( PREFIX+"/packages/"+package+"/"+version+"/"+package+"-"+version+"/"+ package+"-"+version+".dirs.dat","r")
    k.FILES = pickle.load(f_file)
    k.DIRS = pickle.load(d_file)
    f_file.close()
    d_file.close()
    real_dirs  = [item["path"] for item in k.DIRS]
    real_files = []
    for item in k.FILES:
        if item["with_sub_dir"]:
            if item["from"].__class__ == [].__class__:
                for frm_file in item["from"]:
                    if item["to"].endswith("/"):
                        real_files.append( os.path.dirname(item["to"]) + "/" + os.path.dirname(os.path.normpath(frm_file))+"/"+os.path.basename(frm_file) )
                    else:
                        real_files.append(  os.path.dirname(item["to"]) + "/" + os.path.dirname(os.path.normpath(frm_file))+"/"+os.path.basename(item["to"]) )
            else:
                if item["to"].endswith("/"):
                    real_files.append(  os.path.dirname(item["to"]) + "/" + os.path.dirname(os.path.normpath(frm_file))+"/"+os.path.basename(item["from"]) )
                else:
                    real_files.append( os.path.dirname(item["to"]) + "/" + os.path.dirname(os.path.normpath(frm_file))+"/"+os.path.basename(item["to"]) )
        else:
            if item["from"].__class__ == [].__class__:
                for frm_file in item["from"]:
                    if item["to"].endswith("/"):
                        real_files.append(   item["to"]+os.path.basename(frm_file) )
                    else:
                        real_files.append(  item["to"] )
            else:
                if item["to"].endswith("/"):
                    real_files.append( item["to"]+os.path.basename(item["from"]) )
                else:
                    real_files.append( item["to"] )
    return {"files":real_files,"dirs":real_dirs}
    

def turn_off_cron_package(package):
    '''shutdown the crontab tasks of a specific package'''
    cx = _get_db()
    cu = cx.cursor()
    #先把存在cron的用户列出来;
    cx = _get_db()
    cu = cx.cursor()
    cu.execute("select package,version from packages where cron_status='on'")
    rows = cu.fetchall()
    users = {}
    for row in rows:
        package,version = row
        k=_package_config(package,version)
        for cron in k.CRONTABS:
            if not users.has_key(cron["user"]):
                users[cron["user"]]=1

    for user in users:
        print "delete crontab for user:"+user
        os.popen("crontab -r -u "+user)

    cu.execute("update packages set  cron_status='off' where package='"+package+"' ")
    cx.commit()
    rebuild_cron()

def turn_on_cron_package(package):
    '''shutdown the crontab tasks of a specific package'''
    cx = _get_db()
    cu = cx.cursor()
    cu.execute("update packages set  cron_status='on' where package='"+package+"' ")
    cx.commit()
    rebuild_cron()

def cron_content_of_package(package,version):
    """Show Crontab Content of a Package"""
    k=_package_config(package,version)
    user_crontabs = {}
    for cron in k.CRONTABS:
        if user_crontabs.has_key(cron["user"]):
            user_crontabs[cron["user"]].push(cron)
        else:
            user_crontabs[cron["user"]]=[]
            user_crontabs[cron["user"]].append(cron)
    user_crontab_lines = {}    
    for user in user_crontabs:
        lines = []
        for row in user_crontabs[user]:
            if len(row["mail_to"])>0:
                lines.append("MAIL_TO='"+row["mail_to"]+"'")
            lines.append(row["rule"]+" "+ row["command"])
        user_crontab_lines[user]=lines
    return user_crontab_lines

def rebuild_cron():
    '''rebuild the crontab tasks for all packages'''
    cx = _get_db()
    cu = cx.cursor()
    cu.execute("select package,version from packages where cron_status='on'")
    rows = cu.fetchall()
    user_crontabs = {}
    for row in rows:
        package,version = row
        print "package:",package
        k=_package_config(package,version)
        for cron in k.CRONTABS:
            if user_crontabs.has_key(cron["user"]):
                user_crontabs[cron["user"]].push(cron)
            else:
                user_crontabs[cron["user"]]=[]
                user_crontabs[cron["user"]].append(cron)
    user_files ={}
    import tempfile,os
    for user in user_crontabs:
        lines = []
        for row in user_crontabs[user]:
            if len(row["mail_to"])>0:
                lines.append("MAIL_TO='"+row["mail_to"]+"'")
            lines.append(row["rule"]+" "+ row["command"])
        user_files[user]=lines
         
    for user in user_files:
        str = "\n".join(user_files[user])
        f = tempfile.mkstemp()
        fd = open(f[1],"w")
        fd.write(str+"\n")
        fd.close()
        os.popen("crontab -r -u "+user)
        os.popen("crontab -u "+user + " " + f[1])

def init_supervise(package,version):
    '''initialize files for supervise to make sure some process allways running'''
    k=_package_config(package,version)
    for service in k.SERVICES:
        dir_name = PREFIX+"/packages/"+package+"/"+version  +"/supervise/"
        #+service["name"]
        try:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
        except Exception,e:
            print "e",e
        str = '[program:%s-%s]\ncommand=%s\nautostart=true\nstartsecs=1\nuser=%s\nredirect_stderr=true\nstdout_logfile=%s\n' % (package,service["name"],service["command"],service["user"],service["log"])
        f = open(dir_name + "/" + service["name"]+".conf","w+")
        f.write(str)
        f.close()
        _copy(dir_name+"/"+service["name"]+".conf",SUPERVISOR_CONF_DIR)

#@todo
def run_supervise(package,version):
    """start several supervise process to manage main process"""
    k=_package_config(package,version)
    for service in k.SERVICES:
        dir_name = PREFIX+"/packages/"+package+"/"+version  +"/supervise/"+service["name"]+"/"
        #child process,run "supervice [path]" 
        os.popen("supervise "+dir_name+" &")
    pass

def _copy(source,destination,dest_same_tree=False,chown="root",chmod=0644,ignored_prefix="/"):
    '''copy a file from source to destination'''
    if not os.path.isdir(os.path.dirname(destination)):
        try:
            os.makedirs(os.path.dirname(destination))
        except Exception,e:
            pass

    if os.path.isdir(source):
        return False
    if dest_same_tree == False:
        if destination.endswith("/"):
            if not os.path.isdir(destination):
                try:
                    os.makedirs(destination)
                except:
                    pass
            try:
                log.debug("[cmd] cp "+source + " "+ destination+os.path.basename(source))
                shutil.copyfile(source,destination + os.path.basename(source))
                os.chmod(destination+os.path.basename(source),chmod)
                os.system("chown "+chown+" "+ destination+os.path.basename(source))
            except Exception,cpy_err:
                print "error catched while copy files" % cpy_err
        else:
            try:
                log.debug("[cmd] cp "+source + " "+ destination)
                shutil.copyfile(source,destination)
                os.chmod(destination,chmod)
                os.system("chown "+chown+" " + destination)
            except Exception,cpy_err:
                print "error catched while copy files" % cpy_err


    else:
        normed_path = os.path.normpath(source)
        normed_ignored_prefix = os.path.normpath(ignored_prefix)+"/"
        normed_ignored_prefix = normed_ignored_prefix.replace("//","/")
        normed_path = normed_path.lstrip(normed_ignored_prefix)
        norm_dest = os.path.normpath(destination)
        directory = os.path.dirname(destination)+"/"+os.path.dirname(normed_path)+"/"
        directory = directory.replace("//","/")
        if not os.path.isdir(directory):
            try:
                log.debug("[cmd] makedir "+directory)
                os.makedirs(directory)
            except Exception,e:
                log.error("\t\t\t\tfailed")
                pass
        if destination.endswith("/"):

            if not os.path.isdir( directory):
                try:
                    log.debug("[cmd ] makedir "+ directory)
                    os.makedirs( directory)
                except Exception,e_mkdir:
                    log.error("\t\t\t\tfailed")
                    pass
            try:

                log.debug("[cmd] cp "+source+" " +  directory+os.path.basename(source))
                shutil.copyfile(source, directory+os.path.basename(source))
                os.chmod( directory+"/"+os.path.basename(source), chmod)
                os.system("chown "+chown+" "+ directory+os.path.basename(source))
                log.succ("\t\t\t\tsucceed")
            except Exception,e:
                log.error("\t\t\t\tfailed[may be failed when chmod or chown")
                pass
        else:
            try:
                log.debug("[cmd] cp "+source+" " + os.path.dirname(norm_dest)+"/"+os.path.basename(norm_dest))
                shutil.copyfile(source, os.path.dirname(norm_dest)+"/"+os.path.basename(norm_dest))
                os.chmod( os.path.dirname(norm_dest)+"/"+os.path.basename(norm_dest),chmod)
                os.system("chown "+chown + " " +  os.path.dirname(norm_dest)+"/"+os.path.basename(norm_dest))
                log.succ("\t\t\t\tsucced")
            except Exception,e:
                log.error("\t\t\t\tfailed[may be failed when chmod or chown")

def create(conf):
    '''create a fccpm package from a python-style package config file'''
    log.debug("parsing configuration file")
    k = prepare_taskfile(conf)
    log.succ( "\t\t\t\tconfiguration file parsed")
#    sys.exit(0)
    pre = "./dist/"
    if not os.path.exists(pre+k.PACKAGE+"-"+k.VERSION):
        try:
            print "[cmd] " + pre+k.PACKAGE+"-"+k.VERSION
            os.makedirs(pre+k.PACKAGE+"-"+k.VERSION)
        except Exception,e:
            print "make dir:"+pre+k.PACKAGE+"-"+k.VERSION + " failed ", "\n"
            pass
    log.debug( "creating direcoties ...")
    pre = pre + k.PACKAGE+"-"+k.VERSION
    for d in k.DIRS:
        try:
            if not os.path.exists(pre+d["path"]):
                log.debug("try to make dir:"+pre+d["path"])
                os.makedirs(pre+d["path"])
        except Exception,e:
            print "Failed because mkdir failed:"+d["path"],e
            return false
            sys.exit(4)
    log.succ("\t\t\t\tdirectories created")
    log.debug( "...copying files to destination dir")
    for f in k.FILES:
        try:
            if f["from"].__class__ == [].__class__ :
                for each_file in f["from"]:
                    if f.has_key("ignored_dir_prefix"):
                        _copy(each_file,pre+f["to"],f["with_sub_dir"],f["chown"],f["chmod"],f["ignored_dir_prefix"])
                    else:
                        _copy(each_file,pre+f["to"],f["with_sub_dir"],f["chown"],f["chmod"])

                    #shutil.copy(each_file,pre+f["to"])
            else:
                log.debug("cp file from "+f["from"]+" to "+pre+f["to"])
                _copy(f["from"],pre+f["to"],f["with_sub_dir"],f["chown"],f["chmod"])
                #shutil.copy(f["from"],pre+f["to"])
        except Exception,e:
            log.error( "Failed because copy file from {"+f["from"] + "} to {"+f["to"]+"} failed" )
            print e
            log.error("Exit now.")
            sys.exit(5)
    print "[cmd] cp "+conf+ " " + pre+".py "
    os.system("cp "+conf+ " " + pre+".py")
    p = k.PACKAGE + "-" + k.VERSION
    try:
        f_files = open(pre+"/"+p+".files.dat","w+")
        d_files = open(pre+"/"+p+".dirs.dat","w+")
        pickle.dump(k.FILES,f_files)
        pickle.dump(k.DIRS,d_files)
        f_files.close()
        d_files.close()
        log.debug( "generating "+pre+"/"+p+".files.dat")
        log.debug( "generating "+pre+"/"+p+".dirs.dat")
    except Exception,e:
        print "error while create picke files",e
    print "[cmd] chdir ./dist/"
    os.chdir("./dist/")
    try:
        print "[cmd] tar -czf "+p+".tar.gz "+p+".py "+p+"/"
        f=os.popen("tar -czf "+p+".tar.gz "+p+".py "+p+"/","r")
    except Exception,e:
        print "error while tar -czf " + p + ".tar.gz "+p+".py "+p+"/"
        return False
    log.debug("package file ./dist/"+p+".tar.gz generated!")
    return True

def install_package(gzfile,package,version):
    '''
    install the package to the system.
    gzfile: the distribution package file .linke ./{package}-{version}.tar.gz
    '''
    
    if not     os.path.isdir(PREFIX+"packages/"+package+"/"+version):
        try:
            log.info("make dir:"+ PREFIX+"packages"+package+"/"+version)
            os.makedirs(PREFIX+"packages/"+package+"/"+version)
            log.succ("\t\t\t\tsucceed")
        except Exception,e:
            log.error("\t\t\t\tfailed")
            log.error(e.message)
            pass
    realpath = os.path.realpath(gzfile)
    #先把gzfile拷到指定的目录;
    if realpath!= PREFIX + "packages/"+package + "/" + version + "/" + os.path.basename(gzfile):
        log.debug("[cmd] cp " + gzfile+" " + PREFIX+"packages/"+package+"/"+version+"/"+os.path.basename(gzfile))
        shutil.copyfile(gzfile, PREFIX+"packages/"+package+"/"+version+"/"+os.path.basename(gzfile))
    else:
        #如果gzip文件指定的就是目标地址的gzip,就不用拷贝了;
        pass
    #print "chdir"+ PREFIX+"packages/"+package+"/"+version+"/"
    os.chdir(PREFIX+"packages/"+package+"/"+version+"/")
    os.system("tar -xzf "+os.path.basename(gzfile))

    #下面要加载
    #os.chdir(PREFIX+"packages/"+package+"/"+version+"/"+package+"-"+version+"/")
    k=prepare_taskfile(package+"-"+version+".py")
    dir_prefix = PREFIX+"packages/"+package+"/"+version+"/"+package+"-"+version+"/"
    
    f_dat = open(dir_prefix+package+"-"+version+".files.dat","r")
    k.FILES = pickle.load(f_dat)
    f_dat.close()

    d_dat = open(dir_prefix+package+"-"+version+".dirs.dat","r")
    k.DIRS = pickle.load(d_dat)
    d_dat.close()

    os.chdir(PREFIX+"packages/"+package+"/"+version+"/"+package+"-"+version+"/")
    #先创建目录
    for directory in k.DIRS:
        if not os.path.exists(directory["path"]):
            try:
                os.makedirs(directory["path"])
                os.chmod(directory["path"],directory["chmod"])
                os.system("chown "+directory["chown"]+" "+directory["path"])
            except Exception,e:
                print "install failed,because :",e
                sys.exit(5)

    #拷贝文件;
    for fl in k.FILES:
        if fl["from"].__class__ != [].__class__ :
            fl["from"]=[fl["from"]]
        for ff in fl["from"]:
            try:
                #hello
                if fl["with_sub_dir"]:
                    if fl.has_key("ignored_dir_prefix"):
                        tmp = "/"+os.path.normpath(ff)
                        tmp = tmp.replace("//","/")
                        tmp = tmp.lstrip( os.path.normpath(fl["ignored_dir_prefix"]))
                        _copy("."+fl["to"]+tmp,fl["to"]+tmp,False,fl["chown"],fl["chmod"])
                    else:
                    #print os.path.normpath(ff).lstrip( os.path.normpath(ff["ignored_dir_prefix"]))
                        _copy("."+fl["to"]+os.path.normpath(ff),fl["to"]+os.path.normpath(ff),False,fl["chown"],fl["chmod"])
                else:
                    if fl["to"].endswith("/"):
                        _copy("."+fl["to"]+os.path.basename(ff),fl["to"]+os.path.basename(ff),False,fl["chown"],fl["chmod"])
                    else:
                        _copy("."+fl["to"]+os.path.basename(ff),fl["to"],False,fl["chown"],fl["chmod"])
            except Exception,e:
                print e
                pass

    #设置权限;
    '''
    for f in k.CHMODS:
        try:
            command = "chown "+f["option"]+ " " +f["chown"] + " " + f["path"]
            os.system(command)
            command = "chmod "+f["option"]+ " " +f["chmod"] + " " + f["path"]
            os.system(command)
            pass
        except Exception,e:
            pass
    pass 
    '''
    log.info("update database......")
    cx = _get_db()
    cu = cx.cursor()
    #先检查该包当前是否已经存在,存在的话就修改;
    try:
        cu.execute("select * from packages where package='"+package + "'")
    except Exception,e:
        log.info(".......db not initialized.Will init it now.")
        init_db()
        cu.execute("select * from packages where package='"+package + "'")

    rs = cu.fetchone()
    if rs==None:
        cu.execute("insert into packages values ('"+package+"','"+version+"','normal','on')")
        cx.commit()
    else:
        cu.execute("update packages set version='"+version+"',status='normal',cron_status='on' where package='"+package + "'")
        cx.commit()
        pass
    log.succ("\t\t\t\tupdated")

def uninstall_package(package,version):
    '''
    uninstall the package to the system.
    gzfile: the distribution package file .linke ./{package}-{version}.tar.gz
    '''

    #下面要加载
    os.chdir(PREFIX+"packages/"+package+"/"+version+"/")
    k=prepare_taskfile(package+"-"+version+".py")
    dir_prefix = PREFIX+"packages/"+package+"/"+version+"/"+package+"-"+version+"/"
    
    os.chdir(PREFIX+"packages/"+package+"/"+version+"/"+package+"-"+version+"/")
    f_dat = open(dir_prefix+package+"-"+version+".files.dat","r")
    k.FILES = pickle.load(f_dat)
    f_dat.close()

    d_dat = open(dir_prefix+package+"-"+version+".dirs.dat","r")
    k.DIRS = pickle.load(d_dat)
    d_dat.close()
    #删除文件;
    for fl in k.FILES:
        if fl["from"].__class__ != [].__class__ :
            fl["from"]=[fl["from"]]
        try:
            for ff in fl["from"]:
                #hello
                if fl["with_sub_dir"]:
                    os.unlink(fl["to"]+os.path.normpath(ff))
                else:
                    if fl["to"].endswith("/"):
                        os.unlink(fl["to"]+os.path.basename(ff))
                    else:
                        os.unlink(fl["to"])
        except Exception,e:
            print "install failed when unlink file:"+fl["to"],e

    #设置权限;
    '''
    for f in k.CHMODS:
        try:
            command = "chown "+f["option"]+ " " +f["chown"] + " " + f["path"]
            os.system(command)
            command = "chmod "+f["option"]+ " " +f["chmod"] + " " + f["path"]
            os.system(command)
            pass
        except Exception,e:
            pass
    pass 
    '''
    cx = _get_db()
    cu = cx.cursor()
    #先检查该包当前是否已经存在,存在的话就修改;
    try:
        cu.execute("delete from packages where package='"+package + "' and version='"+version+"'")
        cx.commit()
    except Exception,e:
        pass

def check_config_file(config_file):
    ''' check the config file,to see if it's right format and have all fields'''
    k = None
    try:
        k = prepare_taskfile(config_file)
    except:
        log.error("config file "+config_file + " load failed,is that a valid Python file?")
        pass
    file_fields = ["from","to","chown","chmod"]
    dir_fields = ["path","chown","chmod"]
    mod_fields = ["path","chown","chmod","option"]
    service_fields = ["name","desc","command","user","log"]
    cron_fields = ["rule","desc","mail_to","user","command"]
    for i in dir_fields:
        for item in k.DIRS:
            if not item.has_key(i):
                log.error("DIRS must have a %s field:" % i)
                print "\t",item
                return False

    for i in file_fields:
        for item in k.FILES:
            if not item.has_key(i):
                log.error("FILES must have a %s field:" % i)
                print "\t",item
                return False
    for i in mod_fields:
        for item in k.CHMODS:
            if not item.has_key(i):
                log.error("CHMODS must have a %s field:" % i)
                print "\t",item
                return False

    for i in service_fields:
        for item in k.SERVICES:
            if not item.has_key(i):
                log.error("SERVICES must have a %s field:" %i)
                print "\t",item
                return False

    for i in cron_fields:
        for item in k.CRONTABS:
            if not item.has_key(i):
                log.error("CRONTABS must have a %s field:" %i)
                print "\t",item
                return False
    return True

def guess_version(package_file_name):
    package_file_name = package_file_name.strip(".tar.gz")
    info = package_file_name.split("-")
    import re
    version_re = re.compile("^[\d\.]+$")
    if len(info)==2 :
        if version_re.match(info[1]):
            return [os.path.basename(info[0]),info[1]]
    return  None

def run_all_supervises():
    '''when the operation startes,run all supervises for every pacakge'''
    packages = list_packges()
    for pacakge in packages:
        name,version,status = pacakge
        print "try to run_supervise for ",name,version
        run_supervise(name,version)

def sed_file(original_file,new_file,str_before,str_after):
    cmd = "sed -e 's/\(\$("+str_before+")\)/"+str_after+"/' " + original_file+" > "+new_file
    log.debug("[cmd] "+cmd)
    os.popen(cmd)

def set_env_variable(package_name,var_name,var_value):
    #get current_version
    version_row = get_current_version(package_name)
    version = version_row[1]
    k = _package_config(package_name,version)

    for file in  k.CONFIG_FILES:
        original_file = PREFIX+"/packages/"+package_name+"/"+version+"/"+package_name+"-"+version+"/" + file
        original_file = original_file.replace("//","/")
        sed_file(original_file,file,var_name,var_value)
        echo "file modifyed,you 'd better check the content:"+ file 
     

if __name__ == "__main__":
    print guess_version("./dist/fccpm-1.0.0.tar.gz")
