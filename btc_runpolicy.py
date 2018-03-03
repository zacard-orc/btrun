# -*- coding:utf-8 -*-
# btctrade

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
    base_url=dom_url+'/market/history/kline?period=1min&size=1&symbol='+kp
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
    krtn=[]
    #读取MA防止数据出错
    while True:
        krtn=insdb.sLoadKLine(o)
        a=krtn[2]['p_ma10']
        if a is  None:
            logger.debug('再取一次')
            time.sleep(1)
        else:
            break

    rprtn = api_getRealTimeKline(kp)
    # print rprtn
    rp=rprtn['data']
    opsrtn= insdb.sBtcLoadLastOps(o)
    new_ma=[]
    new_ma.append(rp[0]['close'])
    for i in range(29):
        new_ma.append(krtn[i+1]['close'])
    # print new_ma
    this_p_ma5=sum(new_ma[:5]) / 5
    this_p_ma10=sum(new_ma[:10]) / 10
    this_p_ma30=sum(new_ma) / 30

    #计算最新的MA5
    grad_v_ma5=(this_p_ma5-krtn[1]['p_ma5'])/4 #对边/邻边
    grad_v_ma10=(this_p_ma10-krtn[1]['p_ma10'])/10
    grad_v_ma30=(this_p_ma30-krtn[1]['p_ma30'])/15
    #
    angle_v_ma5=mUtil.getAngleByKRate(grad_v_ma5)
    angle_v_ma10=mUtil.getAngleByKRate(grad_v_ma10)
    angle_v_ma30 = mUtil.getAngleByKRate(grad_v_ma30)
    #
    logger.debug('ma5角度,'+str(angle_v_ma5)+'  '+str(this_p_ma5)+','+str(krtn[1]['p_ma5']))
    logger.debug('ma10角度,'+str(angle_v_ma10)+'  '+str(this_p_ma10)+','+str(krtn[1]['p_ma10']))
    logger.debug('ma30角度,'+str(angle_v_ma30)+'  '+str(this_p_ma30)+','+str(krtn[1]['p_ma30']))


    # macd_v_last=[]
    # for i in range(8):
    #     macd_v_last.append(krtn[i]['macd'])
    #
    # macd_v_last.reverse()
    # logger.debug('最近7项MACD,'+str(macd_v_last))




api_runpolicy()

# real price / 1min
if os.getenv('PYVV')=='work' and sys.argv[1]=='1min':
    # for i in range(len(kp_coin)):
    api_runpolicy(kp='btcusdt')
    time.sleep(45)
    api_runpolicy(kp='btcusdt')

