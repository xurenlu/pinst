Pinst package management tool.

**Author**:<renlu.xu@gmail.com>

**homepage**:<http://www.162cm.com>

**Version**:1.0.0

#做好用的git管理软件…#


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