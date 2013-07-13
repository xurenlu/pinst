# -*- coding: utf-8 -*-
'''
This module handle php log parsing
@Author renlu 
@Mail renlu.xu@xiaoqianbao.com
'''
import nvwa.pprint
import nvwa.mail
#parse for php log 
def parseLine(l):
    array = l.split(" ")
    try:
        #第一步先检查是否带时间戳格式;
        if array[0][0]=="[" and array[1][-1]=="]" :
            timestamp = array[0][1:]+" " +array[1][:-1]
            if array[2]=="PHP":
                if array[4]=="error:":
                    level = array[3]+" "+ array[4]
                    msg = " ".join(array[5:])
                else:
                    level = array[3]
                    msg = " ".join(array[4:])
            else:
                level = "debug"
                msg = " ".join(array[2:])
            #第5个是error
            if array[2]=="PHP":
                data = {"type":"CREATE","level":level,"data":msg,"time":timestamp}
            else:
                data = {"type":"CREATE","level":level,"data":msg,"time":timestamp}
        else:
            data = {"type":"UPDATE","data":l}
    except:
        #只要出错了的,都是追加的消息;
        data = {"type":"UPDATE","data":l}
        pass
    return data

def parseTengineAccessLine(l):
    array = l.split(" ")
    
     
def parseNginxLine(l):
    array = l.split(" ")
    print array
    try:
        #第一步先检查是否带时间戳格式;
        if array[2][0]=="[" and array[2][-1]=="]" :
            timestamp = array[0]+" " +array[1]
            level = array[2][1:-1]
            msg = " ".join(array[2:])
            #第5个是error
            data = {"type":"CREATE","level":level,"data":msg,"time":timestamp}
        else:
            data = {"type":"UPDATE","data":l}
    except:
        #只要出错了的,都是追加的消息;
        data = {"type":"UPDATE","data":l}
        pass
    return data
