# -*- coding:utf-8 -*-
# 火币 K先为了QE,47.52.131.46

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
dom_url='http://api.huobi.pro'
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
# kp_coin=[]
kp_coin_uniq={}
# kp_coin=['btcusdt','ethusdt','bchusdt','etcusdt','ltcusdt','eosusdt','xrpusdt','dashusdt',
#              'nasusdt','htusdt','hsrusdt','qtumusdt','iostusdt','neousdt','sntusdt',
#              'elaeth','chateth','thetaeth','mdseth','omgeth','storjusdt'
#     ,'ocneth','itceth','dgdeth','evxeth','btmeth']
kp_coin=['ethusdt','btcusdt','bchusdt']

kp_scale=1

#外汇
def wh():
    base_url='https://finance.yahoo.com/webservice/v1/symbols/allcurrencies/quote'
    resHttpText = mHTTP.spyHTTP3(p_url=base_url)
    constct_html = BeautifulSoup(resHttpText, 'lxml')
    res=constct_html.find_all('resource',attrs={'classname':'Quote'})
    for i in range(len(res)):
        fd=res[i].find('field',attrs={'name':'name'})
        if fd.text==u'USD/CNY':
            fd = res[i].find('field', attrs={'name': 'price'})
            p_base['usdt']=float(fd.text)
            p_base['sdt']=float(fd.text)
            break

    logger.debug('[FOUND]:usdt='+str(p_base['usdt']))

    base_url = dom_url + '/market/history/kline?period=1min&size=1&symbol='+'ethusdt'
    resHttpText = mHTTP.spyHTTP3(p_url=base_url)
    rtn=json.loads(resHttpText)
    data = rtn['data']
    p_base['eth']=data[0]['close']

    base_url = dom_url + '/market/history/kline?period=1min&size=1&symbol=' + 'btcusdt'
    resHttpText = mHTTP.spyHTTP3(p_url=base_url)
    rtn = json.loads(resHttpText)
    data = rtn['data']
    p_base['btc'] = data[0]['close']


#
# def api_merged(kp='btcusdt'):
#     #买1卖1
#     base_url=dom_url+'/market/detail/merged?symbol='+kp
#     resHttpText = mHTTP.spyHTTP3(p_url=base_url)
#     if type(resHttpText) is int:
#         logger.debug('http异常')
#         return -1
#     rtn=json.loads(resHttpText,encoding='utf-8')
#     if rtn['status']<>u'ok':
#         logger.debug('http busi status 异常')
#         return -2
#
#     order_list = rtn['tick']
#     oorder = {}
#     oorder['b1_p'] = order_list['bid'][0]
#     oorder['b1_a'] = order_list['bid'][1]
#     oorder['s1_p'] = order_list['ask'][0]
#     oorder['s1_a'] = order_list['ask'][1]
#     return oorder
#



def api_kline(tp=5,kp='btcusdt'):
    perd=''
    if tp==1:
        perd='1min'
    if tp==5:
        perd='5min'
    if tp==15:
        perd='15min'
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
    his_high=[]
    his_low=[]
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
        his_high.append(o['high'])
        his_low.append(o['low'])

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
    rtn_o['his_high']=max(his_high)
    rtn_o['his_low']=min(his_low)

    dps=api_depth(kp)
    rtn_o['buy_q']=dps[0]
    rtn_o['sell_q']=dps[1]

    return rtn_o



#
# def api_dealhis(kp='btcusdt'):
#     base_url=dom_url+'/market/history/trade?size=300&symbol='+kp
#
#     resHttpText = mHTTP.spyHTTP3(p_url=base_url,p_machinetype='h5')
#     if type(resHttpText) is int:
#         logger.debug('http异常')
#         return -1
#
#     rtn=json.loads(resHttpText)
#     if rtn['status']<>u'ok':
#         return -2
#
#     data=rtn['data']
#     oa={}
#     for i in range(len(data)):
#         udata=data[i]['data']
#         for j in range(len(udata)):
#             ntime=mUtil.UTCtoSTDStamp(udata[j]['ts']/1000)[:16]
#             # print udata[j]
#
#             if oa.has_key(ntime) is False:
#                 oa[ntime] = [0,0,0,0,0]  #买量，卖量，买卖比，买大单，卖大单
#
#             accm=udata[j]['amount']*udata[j]['price']
#             accm_cny=10000
#             if kp[-4:]=='usdt': #则按usdt计价
#                 accm_base=p_base['usdt']
#                 accm=accm*accm_base
#             else:
#                 accm_base=p_base[kp[-3:]]
#                 accm=accm*accm_base*p_base['usdt']
#
#
#             if udata[j]['direction']==u'buy':
#                 oa[ntime][0]+=udata[j]['amount']
#                 # if udata[j]['amount'] >= kp_coin_big[kp]:
#                 if accm>=accm_cny:
#                     oa[ntime][3] += udata[j]['amount']
#             if udata[j]['direction'] == u'sell':
#                 oa[ntime][1] += udata[j]['amount']
#                 if accm>=accm_cny:
#                     oa[ntime][4] += udata[j]['amount']
#
#             if oa[ntime][1]==0:
#                 oa[ntime][2]=0
#             else:
#                 if oa[ntime][0] >= oa[ntime][1]:
#                     oa[ntime][2]=oa[ntime][0]/oa[ntime][1]
#                 else:
#                     if oa[ntime][0] == 0:
#                         oa[ntime][2] = 0
#                     else:
#                         oa[ntime][2]=-oa[ntime][1]/oa[ntime][0]
#
#     dst = datetime.datetime.now() + datetime.timedelta(minutes=-1)
#     dst = dst.strftime("%Y-%m-%d %H:%M")
#     for m in oa:
#         # print m,oa[m]
#         idb={}
#         idb['exn']='HB'
#         idb['kp']=kp
#         idb['kutc']=m+':00'
#         idb['buy_a']=oa[m][0]
#         idb['sell_a']=oa[m][1]
#         idb['sw']=oa[m][2]
#         idb['buy_big_a']=oa[m][3]
#         idb['sell_big_a']=oa[m][4]
#         if m>=dst:
#             insdb.sBtcMarkAccInsert(idb)
#     # dst = datetime.datetime.now() + datetime.timedelta(minutes=-1)
#     # dst = dst.strftime('%Y-%m-%d %H:%M')
#     # rtn_o={}
#     # ##买量，卖量，买卖比，买大单，卖大单
#     # rtn_o['ddtime']=dst
#     # rtn_o['dtl_buy_a']=oa[dst][0]
#     # rtn_o['dtl_sell_a']=oa[dst][1]
#     # rtn_o['dtl_sw']=oa[dst][2]
#     # rtn_o['dtl_buy_big_a']=oa[dst][3]
#     # rtn_o['dtl_sell_big_a']=oa[dst][4]
#
#     # return rtn_o
#
#


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

    #eth一遍
    for j in range(len(rtn)):
        if mUtil.u8(rtn[j]['quote-currency'])=='eth':
            if kp_coin_uniq.has_key(mUtil.u8(rtn[j]['base-currency'])):
                logger.debug('skip kp')
            else:
                kp_coin.append(mUtil.u8(rtn[j]['base-currency'])+mUtil.u8(rtn[j]['quote-currency']))
                kp_coin_uniq[mUtil.u8(rtn[j]['base-currency'])]=True

    #btc一遍
    for j in range(len(rtn)):
        if mUtil.u8(rtn[j]['quote-currency'])=='btc':
            if kp_coin_uniq.has_key(mUtil.u8(rtn[j]['base-currency'])):
                logger.debug('skip kp')
            else:
                kp_coin.append(mUtil.u8(rtn[j]['base-currency'])+mUtil.u8(rtn[j]['quote-currency']))
                kp_coin_uniq[mUtil.u8(rtn[j]['base-currency'])]=True

        # #base-currency,quote-currency
        # if mUtil.u8(rtn[j]['quote-currency'])!='btc':

        # print kp_coin[-1]


def runCollect():
    # sys.argv[1] == 'k1mindtl'
    if len(sys.argv)>1:
        num_split_kp=int(sys.argv[1])
        logger.debug('kp_split:'+sys.argv[1])
        for i in range(len(kp_coin)):
            if i % kp_scale == num_split_kp:
                try:
                    ko1=api_kline(tp=5,kp=kp_coin[i])
                    # ko2=api_merged(kp_coin[i])
                    # api_dealhis(kp_coin[i])
                    dictMerged1 = dict(ko1.items())
                    # dictMerged1 = dict(ko1.items() + ko2.items())

                    dictMerged1['kutc']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:00')
                    insdb.sBtcMarkKline4Q(dictMerged1)
                except Exception,e:
                    logger.debug('[OHS]' + traceback.format_exc())
    else:
        logger.warn('第二入参不存在')


def api_otcusdt():
    sell_base_url='https://otc-api.huobi.br.com/v1/otc/trade/list/public?country=37&currency=1&payMethod=0&currPage=1&coinId=2&tradeType=0&merchant=1&online=1'
    bul_base_url ='https://otc-api.huobi.br.com/v1/otc/trade/list/public?country=37&currency=1&payMethod=0&currPage=1&coinId=2&tradeType=1&merchant=1&online=1'

    pageRtn=mHTTP.spyHTTP3(sell_base_url)
    rtn=json.loads(pageRtn)
    rtn=rtn['data']
    dst = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:00')

    #sell
    # for i in range(0,5):
    #     o={}
    #     o['exn']='HB'
    #     o['kutc']=dst
    #     o['sort_id']=i+1
    #     o['direction']='sell'
    #     o['price']=rtn[i]['price']
    #     o['r_min']=rtn[i]['minTradeLimit']
    #     o['r_max']=rtn[i]['maxTradeLimit']
    #     insdb.sUsdtMarketInsert(o)

    #buy
    pageRtn = mHTTP.spyHTTP3(bul_base_url)
    rtn = json.loads(pageRtn)
    rtn = rtn['data']
    for i in range(0, 1):
        o = {}
        o['exn'] = 'HB'
        o['kutc'] = dst
        o['sort_id'] = i + 1
        o['direction'] = 'buy'
        o['price'] = rtn[i]['price']
        o['r_min'] = rtn[i]['minTradeLimit']
        o['r_max'] = rtn[i]['maxTradeLimit']
        insdb.sUsdtMarketInsert(o)

# def api_depth(kp='btcusdt'):
#     base_url = dom_url + '/market/depth?symbol='+kp+'&type=step5'
#     resHttpText = mHTTP.spyHTTP3(p_url=base_url)
#
#     if type(resHttpText) is int:
#         logger.debug('http异常')
#         return -1
#
#     rtn=json.loads(resHttpText)
#     if rtn['status']<>u'ok':
#         return -2
#
#     data=rtn['tick']
#
#     #买盘
#     bids_data=data['bids']
#     bsum=0
#     for i in range(len(bids_data)):
#         bsum+=bids_data[i][1]
#
#     # 卖盘
#     asks_data = data['asks']
#     asum = 0
#     for i in range(len(asks_data)):
#         asum += asks_data[i][1]
#     return (bsum,asum)

# wh() #外汇
# api_commtxpair()
# api_depth()

#
# print len(kp_coin)
# for i in range(len(kp_coin)):
#     print kp_coin[i]
# time.sleep(111)


logger.debug(os.getenv('PYVV'))
if os.getenv('PYVV')=='work':
    while True:
        try:
            # 暂时不需要获取最新的币对
            # nst = datetime.datetime.now().strftime("%M")
            # if int(nst) % 5 == 0:
            #     kp_coin = []
            #     kp_coin_uniq = {}
                # api_commtxpair()
            if int(sys.argv[1])<=2:
                logger.debug('标记为0的过滤USDT')
                # wh()
                api_otcusdt()
            runCollect()
            time.sleep(30)
        except Exception,e:
            logger.debug('[OHS]' + traceback.format_exc())
            # time.sleep(5)



logger.debug('结束')



