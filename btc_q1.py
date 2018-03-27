# -*- coding:utf-8 -*-
# 火币

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
kp_coin=['btcusdt','bchusdt','ethusdt','neousdt','eosusdt','qtumusdt','etcusdt','ltcusdt','dashusdt']
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

    rtn_o={}
    rtn_o['kp']=kp
    rtn_o['exn']='HB'
    rtn_o['p_ma5']=ma_raw[0]['p_ma5']
    rtn_o['p_ma30']=ma_raw[0]['p_ma30']
    rtn_o['p_ma60']=ma_raw[0]['p_ma60']
    rtn_o['angle_v_ma5']= mUtil.getAngleByKRate(grad_v_ma5)
    rtn_o['angle_v_ma30']= mUtil.getAngleByKRate(grad_v_ma30)
    rtn_o['angle_v_ma60']= mUtil.getAngleByKRate(grad_v_ma60)
    rtn_o['close']=ma_raw[0]['close']

    dps=api_depth(kp)
    rtn_o['buy_q']=dps[0]
    rtn_o['sell_q']=dps[1]

    return rtn_o




def api_dealhis(kp='btcusdt'):
    base_url=dom_url+'/market/history/trade?size=2000&symbol='+kp

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
            # print udata[j]

            if oa.has_key(ntime) is False:
                oa[ntime] = [0,0,0,0,0]  #买量，卖量，买卖比，买大单，卖大单

            accm=udata[j]['amount']*udata[j]['price']
            accm_cny=10000
            if kp[-4:]=='usdt': #则按usdt计价
                accm_base=p_base['usdt']
                accm=accm*accm_base
            else:
                accm_base=p_base[kp[-3:]]
                accm=accm*accm_base*p_base['usdt']


            if udata[j]['direction']==u'buy':
                oa[ntime][0]+=udata[j]['amount']
                # if udata[j]['amount'] >= kp_coin_big[kp]:
                if accm>=accm_cny:
                    oa[ntime][3] += udata[j]['amount']
            if udata[j]['direction'] == u'sell':
                oa[ntime][1] += udata[j]['amount']
                if accm>=accm_cny:
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

    # dst = datetime.datetime.now() + datetime.timedelta(minutes=-1)
    # dst = dst.strftime("%Y-%m-%d %H:%M")
    # for m in oa:
    #     # print m,oa[m]
    #     idb={}
    #     idb['exn']='HB'
    #     idb['kp']=kp
    #     idb['kutc']=m+':00'
    #     idb['buy_a']=oa[m][0]
    #     idb['sell_a']=oa[m][1]
    #     idb['sw']=oa[m][2]
    #     idb['buy_big_a']=oa[m][3]
    #     idb['sell_big_a']=oa[m][4]
    #     if m>=dst:
    #         insdb.sBtcMarkAccInsert(idb)



def api_depth(kp='btcusdt'):
    base_url = dom_url + '/market/depth?symbol='+kp+'&type=step5'
    resHttpText = mHTTP.spyHTTP3(p_url=base_url)

    if type(resHttpText) is int:
        logger.debug('http异常')
        return -1

    rtn=json.loads(resHttpText)
    if rtn['status']<>u'ok':
        return -2

    data=rtn['tick']

    #买盘
    bids_data=data['bids']
    bsum=0
    for i in range(len(bids_data)):
        bsum+=bids_data[i][1]

    # 卖盘
    asks_data = data['asks']
    asum = 0
    for i in range(len(asks_data)):
        asum += asks_data[i][1]
    return (bsum,asum)

# wh() #外汇
# api_commtxpair()
# api_depth()


api_kline()
# api_dealhis()
# time.sleep(111)
logger.debug(os.getenv('PYVV'))




logger.debug('结束')



