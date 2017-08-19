#-*- coding:utf-8 -*-
#     NAME:      mUtil.py
#     PURPOSE:   常用的一些工具函数
#     AUTHOR:    Lin Leiying
#     CREATE:    2017/05/26 21:37

import  hashlib,random,re,time,datetime

link = re.compile("(</?(a|i|s)? .*['|\"]>)*")

def getMyCookie():
    m2 = hashlib.md5()
    seed=random.uniform(1,100)
    m2.update(str(seed))
    xseed=m2.hexdigest()
    basecookie='_T_WM='+xseed+'; M_WEIBOCN_PARAMS=featurecode%3D20000181%26fid%3D100505'+'%26uicode%3D10000011'
    return basecookie


def genFateIP():
    unitlist=range(1,253)
    unitip = random.sample(unitlist,4)
    unitip[0]=str(unitip[0])
    unitip[1]=str(unitip[1])
    unitip[2]=str(unitip[2])
    unitip[3]=str(unitip[3])
    return '.'.join(unitip)

def washWeiboText(str):
    s1=re.sub(link,'',str)
    s1=s1.replace('</a>','').replace('<br/>','')
    return s1

def random_str(y):
    return ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890',y))

def random_num():
    return str(int(time.time())*1000000+datetime.datetime.now().microsecond)

def u8(o):
    return o.encode('utf-8')

def UTCtoSTDStamp(a):
    dtstr = '1970-01-01 00:00:00'
    utcstartstamp=datetime.datetime.strptime(dtstr, "%Y-%m-%d %H:%M:%S")
    comafterstamp=utcstartstamp+datetime.timedelta(seconds=int(a),hours=8)
    return comafterstamp.strftime("%Y-%m-%d %H:%M:%S")