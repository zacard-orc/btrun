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
    resHttpText = mHTTP.spyHTTP3(p_url='http://api.huobi.com/staticmarket/ticker_btc_json.js',p_machinetype='h5')
    if type(resHttpText) is int:
        logger.debug('http异常')
    else:
        constct_json = json.loads(resHttpText, encoding='utf-8')
        o={}
        o['time']=int(constct_json['time'])
        o['last']=constct_json['ticker']['last']
        o['vol']=int(constct_json['ticker']['vol'])
        o['vol_delta']=0
        o['updateAt']=mUtil.UTCtoSTDStamp(o['time'])
        sdb.sBtcMarkInsert(o)





def api_k5():
    resHttpText = mHTTP.spyHTTP3(p_url='http://api.huobi.com/staticmarket/btc_kline_005_json.js',p_machinetype='h5')
    if type(resHttpText) is int:
        logger.debug('http异常')
    else:
        constct_json = json.loads(resHttpText, encoding='utf-8')
        for i in range(len(constct_json)):
            o={}
            o['ddtime']=constct_json[i][0]
            o['open']=constct_json[i][1]
            o['high']=constct_json[i][2]
            o['low']=constct_json[i][3]
            o['close']=constct_json[i][4]
            o['vol']=constct_json[i][5]
            sdb.sBtcMarkK5(o)

#utc,price,amount,tid,dltype,updateAt
def api_dealhis():
    resHttpText = mHTTP.spyHTTP3(p_url='http://api.huobi.com/staticmarket/detail_btc_json.js',p_machinetype='h5')
    if type(resHttpText) is int:
        logger.debug('http异常')
    else:
        constct_json = json.loads(resHttpText, encoding='utf-8')
        const_trades=constct_json['trades']
        for i in range(len(const_trades)):
            o={}
            o['utc']=str(const_trades[i]['ts'])
            o['price']=const_trades[i]['price']
            o['amount']=const_trades[i]['amount']
            o['tid']=str(const_trades[i]['tradeId'])
            o['dltype']=const_trades[i]['direction']
            o['updateAt']=mUtil.UTCtoSTDStamp(int(o['utc'])/1000)
            sdb.sBtcDealHis(o)


api_market()
api_k5()
api_dealhis()

crinterval=30 #15秒

while True:
    Timer(crinterval, api_market,()).start()
    Timer(crinterval, api_dealhis,()).start()
    Timer(crinterval, api_k5,()).start()
    logger.debug('wait '+str(crinterval)+' secs to trigger ')
    time.sleep(crinterval)

