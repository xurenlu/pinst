# -*- coding: utf-8 -*-
import sys
sys.path.append("../")
try:
    import nvwa
    import glob
    import nvwa.find
except Exception,e:
    print "exception",e
    pass

PACKAGE = "fccpm"
VERSION = "1.0.0"
CONFIG_FILES=[
    "/home/x/etc/redis.conf"
]
#you can modify the content of file /etc/mysql_pass/q1.conf by:
#daddy set q1_htdocs.mysql_host "192.168.1.192"

PREFIX="/home/x/"
ENV={
    #"nginx_root":"/home/x/www/q1.xiaoqianbao.com/",
}
DIRS = [
    {
        "path":PREFIX+"bin/",
        "chown":"root",
        "chmod":0755
    },
    {
        "path":PREFIX+"db/",
        "chown":"root",
        "chmod":0755
    },
    {
        "path":PREFIX+"lib/",
        "chown":"root",
        "chmod":0755
    },
    {
        "path":PREFIX+"etc/",
        "chown":"root",
        "chmod":0755
    }
]
FILES =[
    {
        "from":"./pinst",
        #glob.glob("./bin/*.*"),
        "to":PREFIX+"bin/",
        "chown":"root",
        "chmod":0755,
        "with_sub_dir":False
    },
    {
        "from":"etc/redis.conf",
        "to":PREFIX+"etc/",
        "chown":"root",
        "chmod":0755,
        "with_sub_dir":False
    },
    {
        "from":nvwa.find.find(["find ./nvwa/  -name \"*.py\" -type f "]),
        "to":PREFIX+"lib/",
        "chown":"root",
        "with_sub_dir":True,
        "chmod":0644
    }
    #{
    #    "from":glob.glob("./nvwa/*.py"),
    #    "to":PREFIX+"lib/",
    #    "chown":"root",
    #    "chmod":0755,
    #    "with_sub_dir":True
    #}
]
#这是安装完成后单独设置一些目录的权限,这些目录并不见得需要安装程序来建立;
#同时,程序会不停地检测这些文件的权限,一旦发现该程序的权限发生改变,会发出警示.
CHMODS=[
    {
        "path":PREFIX+"bin/fccpm.py",
        "chown":"root",
        "chmod":"0755",
        "option":""
    }
]
SERVICES  = [

    #{
    #    "name":"snmp",
    #    "desc":"check if snmpd is running",
    #    "command":"snmpd",
    #    "user":"renlu",
    #    "log":"/tmp/snmp.log"
    #},
    
]

CRONTABS = [

    {
        "desc":"check the shop categories",
        "user":"renlu",
        "rule":"* 23,1,3,5 * * * ",
        "command":"/home/x/bin/php /home/x/bin/pinst",
        "mail_to":"demo@qq.com"
    }
]
COMMANDS = {
    "pre_install":[
    ],
    "after_install":[
        PREFIX+"bin/fccpm.py reset_db"
    ],
    "after_update":[
        #"set q1_htdocs.mysql_user 'q1_super_user'"
    ]
}
