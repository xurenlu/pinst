#coding:utf-8
'''
example:
print pcolor.pcolorstr("hello",4,4,4)
print pcolor.pcolorstr("world",pcolor.PHIGHLIGHT,pcolor.PRED,pcolor.PWHITE)
'''
PESC=chr(27)
POFF=0
PHIGHLIGHT=1
PUNDERLINE=4
PFLICKER=5
PINVERSE=7
PHIDDEN=8

PBLACK=0
PRED=1
PGREEN=2
PYELLOW=3
PBLUE=4
PMAUVE=5
PCYAN=6
PWHITE=7


def pcolorstr(mystr,attr,fore,back):
    fore=fore+30
    back=back+40
    temp=PESC+"["+str(attr)+";"+str(fore)+";"+str(back)+"m";
    temp=temp+mystr+PESC+"[0;0;0;m"
    return temp

def white(t):
    print pcolorstr(t,POFF,PWHITE,PBLACK)

def blue(t):
    print pcolorstr(t,POFF,PBLUE,PBLACK)

def red(t):
    print pcolorstr(t,POFF,PRED,PBLACK)

def green(t):
    print pcolorstr(t,POFF,PGREEN,PBLACK)

def yellow(t):
    print pcolorstr(t,POFF,PYELLOW,PBLACK)
