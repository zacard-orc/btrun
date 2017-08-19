# -*- coding:utf-8 -*-
# btctrade


import os, json, thread, mimetypes, smtplib, random, time, traceback, re, urllib,requests
from libs import mHTTP, mBusiLog, mUtil, mEnv, mDBA2
from threading import Timer


sdb = mDBA2.A_SDB()
logger = mBusiLog.myLog(os.path.basename(__file__).split('.')[0] + '.log')
last_vol_delta=0

def api_market():
    global last_vol_delta
    resHttpText = mHTTP.spyHTTP3(p_url='https://api.btctrade.com/api/ticker?coin=btc',p_machinetype='h5')
    if type(resHttpText) is int:
        logger.debug('http异常')
    constct_json = json.loads(resHttpText, encoding='utf-8')
    constct_json['updateAt']=mUtil.UTCtoSTDStamp(constct_json['time'])

    if last_vol_delta==0:
        last_vol_delta=constct_json['vol']
        constct_json['vol_delta']=0
    else:
        constct_json['vol_delta']=constct_json['vol']-last_vol_delta
        last_vol_delta=constct_json['vol']
    sdb.sBtcMarkInsert(constct_json)

def api_dealhis():
    resHttpText = mHTTP.spyHTTP3(p_url='https://api.btctrade.com/api/trades?coin=btc',p_machinetype='h5')
    if type(resHttpText) is int:
        logger.debug('http异常')
    constct_json = json.loads(resHttpText, encoding='utf-8')
    for i in range(len(constct_json)):
        constct_json[i]['date']=int(constct_json[i]['date'])
        constct_json[i]['updateAt']=mUtil.UTCtoSTDStamp(constct_json[i]['date'])
        sdb.sBtcDealHis(constct_json[i])


api_market()
api_dealhis()

crinterval=15 #15秒

while True:
    Timer(crinterval, api_market,()).start()
    Timer(crinterval, api_dealhis,()).start()
    logger.debug('wait 15 secs to trigger ')
    time.sleep(crinterval)

