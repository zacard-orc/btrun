# -*- coding:utf-8 -*-

import urllib, urllib2, logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

username = 'llysonylin2012'
sender = 'llysonylin2012@163.com'
password = 'love1985'
smtp_server = 'smtp.163.com'

receivers = ','.join(['firenews2016@163.com'])


def sendEmail(in_sub, in_content):
    # 邮件内容
    msg = MIMEMultipart()
    msg['Subject'] = in_sub.encode('gbk')
    msg['From'] = sender
    msg['To'] = receivers

    # 文字部分
    puretext = MIMEText(in_content.encode('utf-8'), 'plain', 'utf-8')
    msg["Accept-Language"] = "zh-CN"
    msg["Accept-Charset"] = "ISO-8859-1,utf-8"

    msg.attach(puretext)

    try:
        client = smtplib.SMTP_SSL()
        client.connect(smtp_server)
        client.login(username, password)
        client.sendmail(sender, receivers, msg.as_string())
        client.quit()
        logging.debug('邮件已发送')
    except Exception, e:
        logging.debug(e.message)


# sendEmail(u'你好', u'上海发生')


import time
from apns import APNs, Frame, Payload

def sendIOS():
    apns = APNs(use_sandbox=True, cert_file='public.pem', key_file='private.pem')

    # Send a notification
    token_hex = 'be0bbd1c579635e1817605acc3c615608f80fa89a40b7688ee8a45693a961cde'
    payload = Payload(alert="Hello World!", sound="default", badge=1)
    apns.gateway_server.send_notification(token_hex, payload)