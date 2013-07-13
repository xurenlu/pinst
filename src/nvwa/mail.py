#!/usr/bin/env python
# -*- coding: utf-8 -*-
#导入smtplib和MIMEText
import smtplib
from email.mime.text import MIMEText
#############
#要发给谁，这里发给2个人
#####################
#设置服务器，用户名、口令以及邮箱的后缀
mail_host="smtp.exmail.qq.com"
mail_user="noreply@xiaoqianbao.com"
mail_pass="xuliuqian"
######################
def send_mail(to_list,sub,content):
    '''
    to_list:发给谁
    sub:主题
    content:内容
    send_mail("aaa@126.com","sub","content")
    '''
    msg = MIMEText(content)
    msg['Subject'] = sub
    msg['From'] = mail_user
    msg['To'] = ";".join(to_list)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user,mail_pass)
        s.sendmail(mail_user, to_list, msg.as_string())
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False
if __name__ == '__main__':
    mailto_list=["renlu.xu@xiaoqianbao.com","55547082@qq.com"]
    if send_mail(mailto_list,"subject","content"):
        print "发送成功"
    else:
        print "发送失败"
