# -*- coding:utf-8 -*-
'''
根据MA30开口角来进行策略分布

'''


from __future__ import division
import os,json,sys,time,datetime
import numpy as np
from libs import mHTTP, mBusiLog, mUtil, mEnv, mDBA2
from threading import Timer


insdb = mDBA2.A_SDB()
logger = mBusiLog.myLog(os.path.basename(__file__).split('.')[0] + '.log')
last_vol_delta=0

# base para
dom_url='https://api.huobi.pro'
AccessKeyId='08f4bb11-da3cb5d9-81292c66-f7372'
SignatureMethod='HmacSHA256'
SignatureVersion='2'

#policy参数
gf_pol_name='pol_ma30'
gf_tlz=0.999 #贪婪值，修正MA附近的凸起
gf_ma20defense=1.002


kp_coin=['btcusdt','ethusdt','bchusdt','eosusdt','neousdt']
kp_coin_big={
    'btcusdt':2,
    'ethusdt':5,
    'bchusdt':5,
    'eosusdt':5,
    'neousdt':5,
}

def api_getRealTimeDeal(kp='btcusdt'):
    base_url=dom_url+'/market/trade?symbol='+kp
    resHttpText = mHTTP.spyHTTP3(p_url=base_url)
    if type(resHttpText) is int:
        logger.debug('http异常')
        return -1
    rtn=json.loads(resHttpText,encoding='utf-8')
    if rtn['status']<>u'ok':
        logger.debug('http busi status 异常')
        return -2
    return rtn


def api_getRealTimeKline(kp='btcusdt'):
    base_url=dom_url+'/market/history/kline?period=5min&size=1&symbol='+kp
    resHttpText = mHTTP.spyHTTP3(p_url=base_url)
    if type(resHttpText) is int:
        logger.debug('http异常')
        return -1
    rtn=json.loads(resHttpText,encoding='utf-8')
    if rtn['status']<>u'ok':
        logger.debug('http busi status 异常')
        return -2
    return rtn


def api_runpolicy(kp='btcusdt'):
    o={
        'kp':'btcusdt',
        'tp':'1'
    }
    o['exn'] = 'HB'
    o['vol'] = 1
    api_getRealTimeKline()



api_runpolicy()



