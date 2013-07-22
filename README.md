Pinst package management tool.

**Author**:<renlu.xu@gmail.com>

**homepage**:<http://www.162cm.com>

**Version**:1.0.0

#简单的线上部署管理软件…#
    Pinst初衷是一个简单易用的包管理软件。可以用来打包，发布，安装pinst包。整个软件用python写成.
    功能简介:
        根据配置文件将一系列文件打包成一个tar文件。可以在配置文件里指定拷贝哪些文件，创建哪些目录，哪些文件是配置文件，以及由supervisord控制的service。

##使用方法 ##

#### 打包 ####

>    1 创建一个配置文件(参照src/config/fccpm.py)

>    2 创建模块:pinst create ./src/config/fccpm.py 

>    3 安装生成的包 pinst install ./dist/fccpm-1.0.0.tar.gz

#### 查看已经安装的包 ####

1 **查看已经安装过的所有包**

>pinst list

2 **列出某个包的所有文件** 

>pinst files fccpm

#### 修改配置文件 ####

> sudo pinst set fccpm daemon "run_as_daemon"

#### 开启、关闭某个包里的crontab ####

> pinst cronon fccpm
> pinst cronoff fccpm

#### 打开某个服务的service ####
> pinst run_service fccpm




##几条原则##

1. 当with_sub_dir是True时,FILES["from"]一般应该是用find或glob命令得到的数组;
1. 当FILES["from"]是数组时,with_sub_dirs不见得是True;
1. 如果不知道怎么设置配置文件,可以参照 /home/x/packages/fccpm/1.0.0/fccpm-1.0.0.py 来配置;具体位置可能随版本而变化.

TODO:

>导入某用户的crontab到一个metapackage metapackage的设计;
>
>可以在安装完后修改指定的配置文件的某一项的值;
> 指定某个文件是配置文件.配置文件在安装时默认不被覆盖;
> 自动化命令:在安装包之前,安装之后,更新之前,更新之后运行的命令.
>    pre_install:
>    
>    post_install:
>    
>    pre_update:
>    
>    post_update: 
>   


已知Bug:

1. [***已经解决***]pinst cronon 不管用。

2. 