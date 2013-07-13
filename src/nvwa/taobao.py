# -*- coding: utf-8 -*-
'''
本模块处理和淘宝长链接相关的事宜.
'''
__author__ = "renlu.xu <renlu.xu@xiaoqianbao.com>"
__version__ = "1.0.0"

import urllib,unittest
import urllib2
import time,httplib
import sys
import simplejson as json
#from gearman import *
import base64

#只是一个示例,您可以撰写自己的submitter类;
class JobSubmitter():
    config = {}
    def __init__(self,config={}):
        self.config = config 
        pass
    def get_submit_job_callback(self):
        pass


#通过往日志文件中添加行来提交任务;
class FileJobSubmitter(JobSubmitter):
    def __init__(self,config={"file":"/tmp/jobbus.log"}):
        self.config = config 
        pass
    def get_submit_job_callback(self):
        config = self.config
        def cb(data):
            fp = open(config["file"],"a+")
            try:
                fp.write(json.dumps(data)+"\n")
            except:
                pass
            fp.close()
        return cb
           
#通过gearman提交任务;
class GearmanJobSubmitter(JobSubmitter):
    config = {} 
    def __init__(self,config={"hosts":["localhost"]}):
        self.config=config
        pass
    def get_submit_job_callback(self):
        config = self.config
        def cb(data):
            num_iid = data
            gc = client.GearmanClient(config["hosts"])
            gc.submit_job(data["type"],"%s" % json.dumps(data),background=False,wait_until_complete=False)
            gc.shutdown()
        return cb


#通过HTTP的方式提交任务;
class HTTPJobSubmitter(JobSubmitter):
    config = {}
    def __init__(self,config={"url":"http://localhost:8100/"}):
        self.config=config
        pass
    #使用HTTPJobSubmitter时,传回的参数data必须是一个数组,包含两个项,一个是task,一个是数值;
    def get_submit_job_callback(self):
        config = self.config
        def cb(data):
            try:
                if data["task"]=="update_item":
                    url = config["url"]+ data["task"]+"?"+str(data["num_iid"])
                elif data["task"]=="update_trade":
                    url = config["url"]+data["task"]+"?"+data["seller_nick"]
                print "visit url",url
                ret = urllib2.urlopen(url)
                return  ret.read()
            except Exception,e:
                print "got errror:",e
                pass
        return cb
#通过HTTP的方式提交任务;
class HTTPMsgJobSubmitter(JobSubmitter):
    config = {}
    def __init__(self,config={"url":"http://1.seo.xiaoqianbao.com/pconnect/new_msg"}):
        self.config=config
        pass
    #使用HTTPJobSubmitter时,传回的参数data必须是一个数组,包含两个项,一个是task,一个是数值;
    def get_submit_job_callback(self):
        config = self.config
        def cb(msg_type,msg):
            try:
                req = urllib2.Request(config["url"])
                post_data = msg
                post_data["msg_type"]=msg_type
                #,"msg":msg}
                data = urllib.urlencode(post_data)
                opener =  urllib2.build_opener(urllib2.HTTPCookieProcessor())
                response = opener.open(req,data)
                ret =  response.read()
                print "ret",ret
                return ret
            except Exception,e:
                print "got errror:",e
                pass
        return cb

class ReconnectException():
    '''一个exception,可能是网络中断,也可能是由淘宝服务器端主动发起的.'''

    def __init__(self,string):
        pass

class TaoPerminateConnection():
    '''
    这是一个处理淘宝长链接的类.
    '''
    app_key = "12385304"
    secret = "ace276ee1aa1274768b0a544e9ecdbb9"
    job_submitter = None

    def __init__(self,job_submitter=None,app_key="",secret=""):
        '''app_key 和secret 可以传入自定义的值'''
        if app_key!="" :
            self.app_key = app_key
        if secret!="":
            self.secret = secret
        if job_submitter != None:
            self.job_submitter = job_submitter
        else:
            self.job_submitter = FileJobSubmitter()

    def run(self):
        ''' connect to taobao and execute operations
        不停地连接淘宝,执行相应的操作;
        当接受到一个重连指令的时候,也会出发ReconnectException 来重连;
        '''
        while True:
            try:
                self.runSocket()
            except ReconnectException,e:
                print "got a new ReconnectException ",e
            time.sleep(5)

    def createSign(self,data,secret):
        '''
        计算sign校验码
        data:      要计算的hash(在php中对应一个数组)
        secret:    app的密钥
        '''
        import md5
        keys = sorted(data)
        string = secret
        for key in keys:
            if key!="" and data[key]!="" :
                string += key+data[key]

        m5=md5.new()
        print "to be hexed string",string+secret
        m5.update(string+secret)
        return m5.hexdigest().upper()

    def createStrParam(self,param):
        '''urlencode一下'''
        return urllib.urlencode(param) 
   
    def top_execute(self,method,session,args,files=None):
        '''调用一个TOP请求,返回结果
        method:要调用的top方法,比如taobao.item.get
        session:用户的top_session
        args:传给top方法的参数
        files:要上传的文件hash,暂时不支持;
        '''
        if session == ""  or session == None:
            return None
        paramArray_basic = {
            "method":method,
            "session":session,
            "timestamp":time.strftime("%Y-%m-%d %H:%M:%S"),
            "format":"xml",
            "app_key":self.app_key,
            "v":"2.0",
            "sign_method":"md5",
            "partner_id":"top-sdk-php-20110609"
        }
        tao_api_url="http://gw.api.taobao.com/router/rest?"
        param = {}
        for k,v in paramArray_basic.iteritems():
            param[k]=v
        for k,v in args.iteritems():
            param[k]=v
        sign = self.createSign(param,self.secret)
        param["sign"]=sign
        for key in param:
            print "key:",key," value:",param[key]
        data_str = self.createStrParam(param)
        data_str = data_str + "&sign="+sign
        conn = httplib.HTTPConnection("gw.api.taobao.com",80)
        headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain","Connection":"Keep-Alive"}
        conn.request("POST", "/router/rest", data_str, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return data

    def testTop(self):
        fields = "sid,cid,title,nick,desc"
        nick = "helloasp"
        print self.top_execute("taobao.shop.get","41013289738434de90fe471294bc5a2c3acl6WtS4DI3bd6219296891",
                               {"fields":fields,"nick":nick},
                               {})
        


    def testSort(self):
        data={"hash":"abcd","function":"fetch_data","key":"我的/ "}
        print self.createSign(data,"8422")
        print self.createStrParam(data)

    def handle_msg(self,msg_type,msg):
        '''处理任何一条消息'''
        try:
            '''
            '''
            self.job_submitter.get_submit_job_callback()(msg_type,msg)
        except Exception,e:
            print "got exception when submit a msg",e
        pass

    def handle_item(self,nick,num_iid):
        '''处理宝贝更新'''
        print("item handled %d" % num_iid)
        try:
            self.job_submitter.get_submit_job_callback()({"task":"update_item","num_iid":num_iid,"type":"item"})
        except Exception,e:
            print "got exception",e 
        pass

    def handle_trade(self,seller_nick,buyer_nick,tid):
        '''处理新增订单的通知''' 
        #执行一条这样的语句;username='helloasp' days=0.1 php cron.php trade_exporter fetch_user_trades
        try:
            self.job_submitter.get_submit_job_callback()({"task":"update_trade","tid":tid,"buyer_nick":buyer_nick,"seller_nick":seller_nick,"type":"trade"})
        except Exception,e:
            print "got exception",e 

    def handle_hb(self):
        print "submit job:test"
        pass
        
    def handle_task(self,data):
        '''转发任务到各个具体的函数'''
        print "got new data:",data
        try:
            code = data["code"]
        except Exception,e:
            print ("index error of data"+e)
            return 
        if code == 200:
            '''连接成功,不必处理'''
            return 
        if code == 201:
            #self.handle_hb()
            '''心跳包,不必处理'''
            return 
        if code == 202:
            for key  in data["msg"]:
                self.handle_msg(key,data["msg"][key])
                                    

            #todo
            return
        if code == 203:
            msg = data["msg"]
            self.handle_msg("msg_203",data["msg"])
            return
        if code == 101:
            raise ReconnectException("max connection time error")
            return 
        if code == 102:
            raise ServerUpdateException(data["msg"])
            return
        if code == 103:
            raise ReconnectException("Unkown error need reconnection")
            return
        if code == 104:
            raise ReconnectException("a nother client connected in, this client need to exit")
            return
        if code == 105:
            raise ReconnectException("need to chech the network.")
            return

        pass

    def runSocket(self):
        import socket  
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  

        param  = {
            "app_key":self.app_key,
            "timestamp":time.strftime("%Y-%m-%d %H:%M:%S")
        }
        sign = self.createSign(param,self.secret)
        param["sign"]=sign
        data=self.createStrParam(param)

        out = "POST /stream HTTP/1.1\r\n";
        out = out + "Host: stream.api.taobao.com\r\n";
        out = out + "Content-Type: application/x-www-form-urlencoded\r\n";
        out += "Content-Length: %d\r\n" % len(data);
        out += "Connection: Keep-Alive\r\n\r\n";
        out += data;

        sock.connect(("stream.api.taobao.com",80))  
        sock.send(out)  
        data= sock.recv(1024)  
        lines = data.split("\r\n\r\n")
        real_data = lines[1].split("\r\n")
        if len(real_data)==1:
            obj = json.loads(real_data[0])
        else:
            obj = json.loads(real_data[1])
        if obj["packet"]["code"]==200:
            pass
        else:
            raise ReconnectException("Wrong connect method "+data)
        while 1:
            print "try to got new data:\n"
            data= sock.recv(1024)  
            real_data = data.split("\r\n")[1]
            print "real_data:",real_data
            try:
                obj = json.loads(real_data)
                try:
                    print "try to handle_task:"
                    self.handle_task(obj["packet"])
                except ReconnectException,rep:
                    print("reconnect exception when  handle_task")
                    pass
                except Exception,eb:
                    print("other error when handle_task")
                    print eb
                    pass
            except Exception,e:
                #string unpacked failed,try to close the sock and retry ;
                sock.close()
                raise ReconnectException("Wrong data received"+data)
            time.sleep(0.1)
        sock.close()  



def test():
    tpc = TaoPerminateConnection()
    tpc.run()
    pass

if __name__ == "__main__":
    #test() 
    #打开授权
    taobao = TaoPerminateConnection(HTTPJobSubmitter(),"12464279","04d98de8e1a5c7327b7de320df1692d7")
    #print taobao.top_execute("taobao.increment.customer.permit","6100c13bcf4962315342a1e671d9cefb065fb9877c08cdb21929689",{"type":"notify"})
    taobao.run()
