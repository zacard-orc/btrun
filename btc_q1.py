# -*- coding:utf-8 -*-
# 火币 米匡-K线

from __future__ import division
import os,json,sys,time,xml,datetime,traceback,thread
import numpy as np
from libs import mHTTP, mBusiLog, mUtil, mEnv, mDBA2
from bs4 import  BeautifulSoup

# time.sleep(111)


insdb = mDBA2.A_SDB()
logger = mBusiLog.myLog(os.path.basename(__file__).split('.')[0] + '.log')
last_vol_delta=0

# base para
dom_url='http://api.huobipro.com'
AccessKeyId='08f4bb11-da3cb5d9-81292c66-f7372'
SignatureMethod='HmacSHA256'
SignatureVersion='2'


kp_coin_big={
    'btcusdt':2,
    'ethusdt':5,
    'bchusdt':5,
    'eosusdt':5,
    'neousdt':5,
}
p_base={
    'usdt':6.35,
    'btc':1,
    'eth':1
}
kp_coin=['btcusdt','bchusdt','ethusdt','neousdt','eosusdt','qtumusdt','etcusdt','ltcusdt','dashusdt','abteth','xrpusdt','itceth','btmeth','omgeth','storjusdt','iostusdt']
kp_coin_uniq={}
# kp_coin=['btcusdt','ethusdt','bchusdt','etcusdt','ltcusdt','eosusdt','xrpusdt','dashusdt',
#              'nasusdt','htusdt','hsrusdt','qtumusdt','iostusdt','neousdt','sntusdt',
#              'elaeth','chateth','thetaeth','mdseth','omgeth','storjusdt'
#     ,'ocneth','itceth','dgdeth','evxeth','btmeth']
kp_scale=5



def api_merged(kp='btcusdt'):
    #买1卖1
    base_url=dom_url+'/market/detail/merged?symbol='+kp
    resHttpText = mHTTP.spyHTTP3(p_url=base_url)
    if type(resHttpText) is int:
        logger.debug('http异常')
        return -1
    rtn=json.loads(resHttpText,encoding='utf-8')
    if rtn['status']<>u'ok':
        logger.debug('http busi status 异常')
        return -2

    order_list = rtn['tick']
    oorder = {}
    oorder['b1_p'] = order_list['bid'][0]
    oorder['b1_a'] = order_list['bid'][1]
    oorder['s1_p'] = order_list['ask'][0]
    oorder['s1_a'] = order_list['ask'][1]
    return oorder




def api_kline(tp=5,kp='btcusdt'):
    perd=''
    if tp==1:
        perd='1min'
    if tp==5:
        perd='5min'
    if tp==15:
        perd='15min'
    if tp==60:
        perd='60min'
    if tp==3600:
        perd='1day'

    base_url=dom_url+'/market/history/kline?period='+perd+'&size=70&symbol='+kp

    resHttpText = mHTTP.spyHTTP3(p_url=base_url)
    if type(resHttpText) is int:
        logger.debug('http异常')
        return -1
    rtn=json.loads(resHttpText,encoding='utf-8')
    if rtn['status']<>u'ok':
        logger.debug('http异常')
        return -2


    data=rtn['data']

    ma_raw=[]

    for i in range(len(data)):
        # print data[i]
        o={}
        o['exn']='HB'
        o['tp']=str(tp)
        o['kp']=kp
        o['kutc']=mUtil.UTCtoSTDStamp(data[i]['id'])
        o['amount']=data[i]['amount'] #成交量
        o['count']=data[i]['count'] #笔数
        o['vol']=data[i]['vol'] #成交额
        o['high']=data[i]['high']
        o['low']=data[i]['low']
        o['open']=data[i]['open']
        o['close']=data[i]['close']
        ma_raw.append(o)


    for i in range(len(ma_raw)):
        if i>5:
            continue
        p_ma5_list=[]
        p_ma30_list=[]
        p_ma60_list=[]

        for j in range(i,len(ma_raw)):
            if (len(ma_raw)-i>30):
                ma_flag=True
                # print j,ma_raw[j]
                if j<i+5:
                    p_ma5_list.append(ma_raw[j]['close'])
                    p_ma30_list.append(ma_raw[j]['close'])
                    p_ma60_list.append(ma_raw[j]['close'])

                if j>=i+5 and j<i+30:
                    p_ma30_list.append(ma_raw[j]['close'])
                    p_ma60_list.append(ma_raw[j]['close'])

                if j>=i+30 and j<i+60:
                    p_ma60_list.append(ma_raw[j]['close'])
        #10,30,60
        ma_raw[i]['p_ma5']=sum(p_ma5_list)/5
        ma_raw[i]['p_ma30']=sum(p_ma30_list)/30
        ma_raw[i]['p_ma60']=sum(p_ma60_list)/60

        # print ma_raw[i]['kp'],ma_raw[i]['kutc'],ma_raw[i]['p_ma10']
        '''
        naseth 2018-02-16 08:05:00 0.009927
        naseth 2018-02-16 08:00:00 0.0099291
        naseth 2018-02-16 07:55:00 0.0099323
        naseth 2018-02-16 07:50:00 0.0099394
        naseth 2018-02-16 07:45:00 0.0099424
        naseth 2018-02-16 07:40:00 0.0099439
        '''

    side=ma_raw[0]['close']*0.001
    grad_v_ma5=(ma_raw[0]['p_ma5']-ma_raw[1]['p_ma5'])/side
    grad_v_ma30=(ma_raw[0]['p_ma30']-ma_raw[1]['p_ma30'])/side
    grad_v_ma60=(ma_raw[0]['p_ma60']-ma_raw[1]['p_ma60'])/side

    ma_raw[1]['angle_v_ma5']= mUtil.getAngleByKRate(grad_v_ma5)
    ma_raw[1]['angle_v_ma30']= mUtil.getAngleByKRate(grad_v_ma30)
    ma_raw[1]['angle_v_ma60']= mUtil.getAngleByKRate(grad_v_ma60)

    insdb.sDataRQInsertKLine(ma_raw[1])



logger.debug(os.getenv('PYVV'))

for i in range(len(kp_coin)):
    try:
        api_kline(5,kp_coin[i])
        # api_kline(15,kp_coin[i])
        # api_kline(60,kp_coin[i])

    except Exception,e:
        logger.debug('[OHS]' + traceback.format_exc())

logger.debug('结束')



