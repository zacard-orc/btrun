# -*- coding:utf-8 -*-


from __future__ import division
import os,json,sys,time,xml,datetime,traceback,thread
import numpy as np
from libs import mHTTP, mBusiLog, mUtil, mEnv, mDBA2
from bs4 import  BeautifulSoup
# import ssl
# context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_0)

# time.sleep(111)

insdb = mDBA2.A_SDB()
logger = mBusiLog.myLog(os.path.basename(__file__).split('.')[0] + '.log')


#USDT
usdtrtn=insdb.sLoadUsdtKline()
p_high=0
p_low=999999
p_open=usdtrtn[0]['price']
p_close=usdtrtn[-1]['price']
p_ambuy=0
p_amsell=0
for i in range(len(usdtrtn)):
    if usdtrtn[i]['price']>p_high:
        p_high=usdtrtn[i]['price']
    if usdtrtn[i]['price']<p_low:
        p_low=usdtrtn[i]['price']
o={}
o['ddtime']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
o['kp']='5'
o['symbol']='USDT'
o['open']=p_open
o['close']=p_close
o['high']=p_high
o['low']=p_low
o['ambuy']=p_ambuy
o['amsell']=p_amsell
insdb.sInsertNMWKline(o)


#其他币种
symList=['ethusdt','btcusdt']
for i in range(len(symList)):
    dbrtn=insdb.sLoadEthKline({'kp':symList[i]})
    p_high=0
    p_low=999999
    p_open=dbrtn[0]['close']
    p_close=dbrtn[-1]['close']
    p_ambuy=0
    p_amsell=0
    for j in range(len(dbrtn)):
        if dbrtn[j]['close']>p_high:
            p_high=dbrtn[j]['close']
        if dbrtn[j]['close']<p_low:
            p_low=dbrtn[j]['close']
        p_ambuy+=dbrtn[j]['buy_q']
        p_amsell+=dbrtn[j]['sell_q']
    o={}
    o['ddtime']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    o['kp']='5'
    o['symbol']=symList[i].split('usdt')[0].upper()
    o['open']=p_open
    o['close']=p_close
    o['high']=p_high
    o['low']=p_low
    o['ambuy']=p_ambuy
    o['amsell']=p_amsell
    insdb.sInsertNMWKline(o)
