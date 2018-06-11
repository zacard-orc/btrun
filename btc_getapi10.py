# -*- coding:utf-8 -*-
# 火币 K历史K线

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
last_vol_delta=0

# base para
dom_url='https://api.huobi.pro'
# dom_url='https://api.hadax.com'

AccessKeyId='08f4bb11-da3cb5d9-81292c66-f7372'
SignatureMethod='HmacSHA256'
SignatureVersion='2'


kp_coin=[]
kp_coin_uniq={}


proxies = {'http':'http://47.52.19.237:3128','https':'http://47.52.19.237:3128'}


def api_commtxpair():
    base_url=dom_url+'/v1/common/symbols'

    resHttpText = mHTTP.spyHTTP3(p_url=base_url,p_machinetype='h5')
    if type(resHttpText) is int:
        logger.debug('http异常')
        return -1

    rtn=json.loads(resHttpText)
    if rtn['status']<>u'ok':
        return -2

    rtn=json.loads(resHttpText)
    rtn=rtn['data']

    #usdt一遍
    for j in range(len(rtn)):
        if mUtil.u8(rtn[j]['quote-currency'])=='usdt':
            kp_coin.append(mUtil.u8(rtn[j]['base-currency']) + mUtil.u8(rtn[j]['quote-currency']))
            kp_coin_uniq[mUtil.u8(rtn[j]['base-currency'])] = True



def api_dealhis(kp='btcusdt'):
    base_url=dom_url+'/market/history/trade?size=400&symbol='+kp

    resHttpText = mHTTP.spyHTTP3(p_url=base_url,p_machinetype='h5')
    if type(resHttpText) is int:
        logger.debug('http异常')
        return -1

    rtn=json.loads(resHttpText)
    if rtn['status']<>u'ok':
        return -2

    data=rtn['data']
    oa={}
    for i in range(len(data)):
        udata=data[i]['data']
        for j in range(len(udata)):
            ntime=mUtil.UTCtoSTDStamp(udata[j]['ts']/1000)[:16]
            # logger.debug(ntime)

            if oa.has_key(ntime) is False:
                oa[ntime] = [0,0,0,0,0]  #买量，卖量，买卖比，买大单，卖大单

            accm=udata[j]['amount']*udata[j]['price']
            limit_usdt=10000 # 等于6.5W RMB

            if udata[j]['direction']==u'buy':
                oa[ntime][0]+=udata[j]['amount']
                # if udata[j]['amount'] >= kp_coin_big[kp]:
                if accm>=limit_usdt: #大单
                    oa[ntime][3] += udata[j]['amount']
            if udata[j]['direction'] == u'sell':
                oa[ntime][1] += udata[j]['amount']
                if accm>=limit_usdt: #大单
                    oa[ntime][4] += udata[j]['amount']


            if oa[ntime][1]==0:
                oa[ntime][2]=0
            else:
                if oa[ntime][0] >= oa[ntime][1]:
                    oa[ntime][2]=oa[ntime][0]/oa[ntime][1]
                else:
                    if oa[ntime][0] == 0:
                        oa[ntime][2] = 0
                    else:
                        oa[ntime][2]=-oa[ntime][1]/oa[ntime][0]

    logger.debug('先判断时间，去除头尾')
    tmpList=[]
    for m in oa:
        tmpList.append(m)

    tmpList.sort(reverse=True)
    logger.debug(tmpList)

    for m in oa:
        # print m,oa[m]
        if m==tmpList[0] or m==tmpList[-1]:
            continue
        idb={}
        idb['exn']='HB'
        idb['kp']=kp.split('usdt')[0].upper()
        idb['kutc']=m+':00'
        idb['buy_a']=oa[m][0]
        idb['sell_a']=oa[m][1]
        idb['sw']=oa[m][2]
        idb['buy_big_a']=oa[m][3]
        idb['sell_big_a']=oa[m][4]
        insdb.sBtcMarkAccInsert(idb)





def api_kline(tp=5,kp='btcusdt'):
    perd=''
    if tp==1:
        perd='1min'
    if tp==5:
        perd='5min'
    if tp==3600:
        perd='1day'

    base_url=dom_url+'/market/history/kline?period='+perd+'&size=10&symbol='+kp

    resHttpText = mHTTP.spyHTTP3(p_url=base_url)
    if type(resHttpText) is int:
        logger.debug('http异常')
        return -1
    rtn=json.loads(resHttpText,encoding='utf-8')
    if rtn['status']<>u'ok':
        logger.debug('http异常')
        return -2


    data=rtn['data']


    for i in range(len(data)):
        # print data[i]
        o={}
        o['exg']='HB'
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

        insdb.sBtcMarkKlineNMW(o)

    api_dealhis(kp)







def runCollect():
    for i in range(len(kp_coin)):
        try:
            # print kp_coin
            api_kline(tp=5,kp=kp_coin[i])
            time.sleep(1)
        except Exception,e:
            logger.debug('[OHS]' + traceback.format_exc())



# api_commtxpair()
logger.debug(os.getenv('PYVV'))
while True:
    try:
        kp_coin = []
        kp_coin_uniq = {}
        api_commtxpair()
        runCollect()

        time.sleep(60)
    except Exception,e:
        tk_msg = traceback.format_exc()
        logger.debug('[OHS],' + tk_msg)






