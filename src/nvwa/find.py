# -*- coding: utf-8 -*-
import sys
from subprocess import *

def find(cmd):
    """
    usage: nvwa.find(["find","./"," -name \"*.py\""])
    """
    #cmd = ["find","./"," -name \"*.py\""]
    p = Popen(cmd,shell=True,bufsize=1024,stdout=PIPE,stdin=PIPE)
    lines = [] 
    while True:
        out = p.stdout.readline()
        if out == '' and p.poll() != None:
            break
        if out != '':
            lines.append(out.strip())
    return lines
