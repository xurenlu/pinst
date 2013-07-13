# coding: utf-8
#
# 这是根据xmpp封装的Jabber聊天机器人类, 可以通过继承,重载部分函数来自定义功能.
# Jabber ID(JID): 比如gamcat@gmail.com

import xmpp

class Bot:
    """ Jabber Bot Base Class """
    JID = ''
    PASSWORD = ''

    client = None   
    def __init__ (self, jid, password):
        self.JID = xmpp.JID(jid)
        self.PASSWORD = password
        self.login(jid,password)

    def login (self,jid,password):         
        self.client = xmpp.Client('gmail.com', debug=[])
        # 连接到google的服务器
        self.client.connect(server=('talk.google.com', 443))
        # 用户身份认证
        self.client.auth(jid,password, 'UDPonNAT')
        if self.client.connect() == '':
            raise 'JabberBot not connected.'
        if self.client.auth(self.JID.getNode(), self.PASSWORD) == None:
            raise 'JabberBot authentication failed.'

        self.client.RegisterHandler('message', self.message_callback)
        self.client.RegisterHandler('presence', self.presence_callback)
        self.client.sendInitPresence()

    def message_callback (self, client, message):
        """ 默认消息回调(可通过继承自定义) """

    def presence_callback (self, client, message):
        """ 默认事件回调,包括下面几个(可通过继承自定义) """
        type = message.getType()
        who = message.getFrom().getStripped()

        if type == 'subscribe':
            self.subscribe(who)
        elif type == 'unsubscribe':
            self.unsubscribe(who)
        elif type == 'subscribed':
            self.subscribed(who)
        elif type == 'unsubscribed':
            self.unsubscribed(who)
        elif type == 'available' or type == None:
            self.available(message)
        elif type == 'unavailable':
            self.unavailable(who)

    def subscribe (self, jid):
        """ 加好友 """
        self.client.send(xmpp.Presence(to=jid, typ='subscribed'))
        self.client.send(xmpp.Presence(to=jid, typ='subscribe'))

    def unsubscribe (self, jid):
        """ 取消好友 """
        self.client.send(xmpp.Presence(to=jid, typ='unsubscribe'))
        self.client.send(xmpp.Presence(to=jid, typ='unsubscribed'))

    def subscribed (self, jid):
        """ 已加 """

    def unsubscribed (self, jid):
        """ 已退 """
      
    def available (self, message):
        """ 上线 """

    def unavailable (self, jid):
        """ 下线 """

    def send (self, jid, message):
        """ 发消息给某人"""
        self.client.send(xmpp.protocol.Message(jid, message))

    def step (self):
        """ 用在循环中 """
        try:
            self.client.Process(1)
        except KeyboardInterrupt:   # Ctrl+C停止
            return False
        return True


#===========================
# 测试
#===========================
class Bot(Bot):
    def message_callback (self, cl, msg):
        fromid = msg.getFrom().getStripped()
        cont = msg.getBody()
        self.send2admin(msg)

    def send2admin (self, message):
        self.send('xurenlu@gmail.com', message)

if __name__ == '__main__':
    gb = Bot('renlu.xu','97386333')
    gb.send2admin ('Bot Started')

    # 开始运行
    #while (gb.step()): pass
