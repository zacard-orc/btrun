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


def sendIOS(list_dev, msg):
    apns = APNs(use_sandbox=True, cert_file='btc123_public.pem', key_file='btc123_private.pem')

    payload = Payload(alert=msg, sound="default", badge=1, content_available=True,
                      custom={'title': u'行情监控'})

    for i in range(len(list_dev)):
        try:
            logging.debug(list_dev[i]['device_token'])
            apns.gateway_server.send_notification(list_dev[i]['device_token'], payload)
            time.sleep(0.5)
        except Exception, e:
            logging.error(e.message)

# sendIOS()
