# -*- coding:utf-8 -*-
# btctrade

from __future__ import division
import os,json,sys,time
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


# kp_coin=['btcusdt','ethusdt','bchusdt','eosusdt','neousdt']
kp_coin_big={
    'btcusdt':2,
    'ethusdt':5,
    'bchusdt':5,
    'eosusdt':5,
    'neousdt':5,
}
kp_coin=[]

# ema计算
def get_EMA(d_list,N):
    logger.debug('处理周期的ema_'+str(N))

    for i in range(len(d_list)):
        # print ''
        # print i, '==>', d_list[i]['kutc']
        if i<25:
            continue

        ema_list=np.zeros(N)
        # print '-------'
        for z in range(N):
            day_id=i-(N-z)+1  #方便从1开始计数,从第前N天开始计算
            # print day_id,'-',d_list[day_id]['kutc'],'-',d_list[day_id]['close']

            if z==0:
                ema_list[z]=(2*d_list[day_id]['close'])/2
            else:
                ema_list[z]=(2*d_list[day_id]['close']+(z+1-1)*ema_list[z-1])/(z+1+1)
        # print ema_list
        d_list[i]['ema_'+str(N)]=round(ema_list[-1],2)
        # time.sleep(0.2)

    return d_list


def get_DIFandDEA(d_list,N):
    logger.debug('处理DIF')
    for i in range(len(d_list)):
        if i < 25:
            continue
        d_list[i]['dif'] = d_list[i]['ema_12'] - d_list[i]['ema_26']

    logger.debug('处理DEA')
    for i in range(len(d_list)):
        if i <25+9:
            continue

        ema_list=np.zeros(N)
        for z in range(N):
            day_id=i-(N-z)+1  #方便从1开始计数,从第前N天开始计算
            if z==0:
                ema_list[z]=(2*d_list[day_id]['dif'])/2
            else:
                ema_list[z]=(2*d_list[day_id]['dif']+(z+1-1)*ema_list[z-1])/(z+1+1)

        d_list[i]['dea']=round(ema_list[-1],2)
        d_list[i]['macd']=round((d_list[i]['dif']-d_list[i]['dea'])*2,2)


    return d_list

def api_merged(kp='btcusdt'):
    base_url=dom_url+'/market/detail/merged?symbol='+kp
    resHttpText = mHTTP.spyHTTP3(p_url=base_url)
    if type(resHttpText) is int:
        logger.debug('http异常')
        return -1
    rtn=json.loads(resHttpText,encoding='utf-8')
    if rtn['status']<>u'ok':
        logger.debug('http busi status 异常')
        return -2

    print rtn
    order_list = rtn['tick']
    oorder = {}
    oorder['exn'] = 'HB'
    oorder['kp'] = kp
    oorder['kutc'] = mUtil.UTCtoSTDStamp(rtn['ts']/1000)
    oorder['price'] = order_list['close']
    oorder['b1_p'] = order_list['bid'][0]
    oorder['b1_a'] = order_list['bid'][1]
    oorder['s1_p'] = order_list['ask'][0]
    oorder['s1_a'] = order_list['ask'][1]
    insdb.sBtcMarkInsert(oorder)


def api_kline(tp=5,kp='btcusdt'):
    perd=''
    if tp==1:
        perd='1min'
    if tp==5:
        perd='5min'

    base_url=dom_url+'/market/history/kline?period='+perd+'&size=100&symbol='+kp

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
        #print o['kutc'] #2018-02-16 07:50:00
        # insdb.sBtcMarkKline(o)

    # ma_raw.reverse()
    # ma_raw=get_EMA(ma_raw,12)
    # ma_raw=get_EMA(ma_raw,26)
    # ma_raw=get_DIFandDEA(ma_raw, 9)
    # ma_raw.reverse()


    for i in range(len(ma_raw)):
    #     if i<25:
    #         omacd = {}
    #         omacd['exn'] = 'HB'
    #         omacd['tp'] = str(tp)
    #         omacd['kp'] = kp
    #         omacd['kutc'] = mUtil.UTCtoSTDStamp(data[i]['id'])
    #         omacd['dif']=ma_raw[i]['dif']
    #         omacd['dea']=ma_raw[i]['dea']
    #         omacd['macd']=ma_raw[i]['macd']
    #         insdb.sBtcMarkKlineMACDUpdate(omacd)

        #     print ma_raw[i]['kutc'],ma_raw[i]['ema_12'],ma_raw[i]['ema_26'],ma_raw[i]['dif'],ma_raw[i]['dea'],ma_raw[i]['macd']
        # print '-------------------'
        p_ma5_list=[]
        p_ma10_list=[]
        p_ma20_list=[]
        p_ma30_list=[]
        v_ma5_list=[]
        v_ma10_list=[]
        ma_flag=False
        for j in range(i,len(ma_raw)):
            if (len(ma_raw)-i>30):
                ma_flag=True
                # print j,ma_raw[j]
                if j<i+5:
                    p_ma5_list.append(ma_raw[j]['close'])
                    p_ma10_list.append(ma_raw[j]['close'])
                    p_ma20_list.append(ma_raw[j]['close'])
                    p_ma30_list.append(ma_raw[j]['close'])
                    # v_ma5_list.append(ma_raw[j]['vol'])
                    # v_ma10_list.append(ma_raw[j]['vol'])

                if j>=i+5 and j<i+10:
                    p_ma10_list.append(ma_raw[j]['close'])
                    p_ma20_list.append(ma_raw[j]['close'])
                    p_ma30_list.append(ma_raw[j]['close'])
                    # v_ma10_list.append(ma_raw[j]['vol'])

                if j>=i+10 and j<i+20:
                    p_ma20_list.append(ma_raw[j]['close'])
                    p_ma30_list.append(ma_raw[j]['close'])
                if j>=i+20 and j<i+30:
                    p_ma30_list.append(ma_raw[j]['close'])

        print p_ma5_list
        print p_ma30_list

    # if ma_flag==True:
        #     o2={}
        #     o2['exn'] = 'HB'
        #     o2['tp'] = str(tp)
        #     o2['kp'] = kp
        #     o2['kutc'] = mUtil.UTCtoSTDStamp(data[i]['id'])
        #     o2['p_ma5']=sum(p_ma5_list)/5
        #     o2['p_ma10']=sum(p_ma10_list)/10
        #     o2['p_ma20']=sum(p_ma20_list)/20
        #     o2['p_ma30']=sum(p_ma30_list)/30
        #     o2['v_ma5']=sum(v_ma5_list)/5
        #     o2['v_ma10']=sum(v_ma10_list)/10
        #     # o2['dif']=ma_raw[i]['dif']
        #     # o2['dea']=ma_raw[i]['dea']
        #     # o2['macd']=ma_raw[i]['macd']
        #     insdb.sBtcMarkKlineMAUpdate(o2)




def api_dealhis(kp='btcusdt'):
    base_url=dom_url+'/market/history/trade?size=500&symbol='+kp

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
            # print ntime
            # print udata[j]
            if oa.has_key(ntime) is False:
                oa[ntime] = [0,0,0,0,0]  #买量，卖量，买卖比，买大单，卖大单

            if udata[j]['direction']==u'buy':
                oa[ntime][0]+=udata[j]['amount']
                if udata[j]['amount'] >= kp_coin_big[kp]:
                    oa[ntime][3] += udata[j]['amount']
            if udata[j]['direction'] == u'sell':
                oa[ntime][1] += udata[j]['amount']
                if udata[j]['amount'] >= kp_coin_big[kp]:
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

    for m in oa:
        # print m,oa[m]
        idb={}
        idb['exn']='HB'
        idb['kp']=kp
        idb['kutc']=m+':00'
        idb['buy_a']=oa[m][0]
        idb['sell_a']=oa[m][1]
        idb['sw']=oa[m][2]
        idb['buy_big_a']=oa[m][3]
        idb['sell_big_a']=oa[m][4]
        insdb.sBtcMarkAccInsert(idb)




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
    for j in range(len(rtn)):
        #base-currency,quote-currency
        # print rtn[j]['base-currency'],rtn[j]['quote-currency']
        kp_coin.append(mUtil.u8(rtn[j]['base-currency'])+mUtil.u8(rtn[j]['quote-currency']))


def runCollect():
    for i in range(len(kp_coin)):
        api_kline(tp=5,kp=kp_coin[i])

api_commtxpair()
runCollect()

# print kp_coin

# real ex detail / 1min
# if os.getenv('PYVV')=='work' and sys.argv[1]=='k1mindtl':
#     for i in range(len(kp_coin)):
#         api_dealhis(kp=kp_coin[i])
#
# # real price / 1min
# if os.getenv('PYVV')=='work' and sys.argv[1]=='merge':
#     for i in range(len(kp_coin)):
#         api_merged(kp=kp_coin[i])
#
# # kline / 1 min
# if os.getenv('PYVV')=='work' and sys.argv[1]=='k1min':
#     for i in range(len(kp_coin)):
#         api_kline(tp=1,kp=kp_coin[i])
#
# # kline / 5 min
# if os.getenv('PYVV')=='work' and sys.argv[1]=='k5min':
#     for i in range(len(kp_coin)):
#         api_kline(tp=5,kp=kp_coin[i])




