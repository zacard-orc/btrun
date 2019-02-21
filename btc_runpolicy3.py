# -*- coding:utf-8 -*-
'''
根据5分钟的MA30，MA60，略线上下位置来比对策
'''


from __future__ import division
import os,json,sys,time,datetime,traceback
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
# gf_pol_name='pol_ma30'
# gf_tlz=0.999 #贪婪值，修正MA附近的凸起
# gf_ma20defense=1.002

gf_pol=[
    {
        'pol_name': 'pol_buy_ma30_offset',
        'pol_desc': 'ma30下方买入',
        'pol_threshold1': -0.3
    },
    {
        'pol_name': 'pol_buy_rushup',
        'pol_desc': '快速上涨开口向上',
        'pol_threshold1': 0.5
    },
    {

    },
    {
        'pol_name': 'pol_sell_inflex',
        'pol_threshold1': 0.2
    },
]


# kp_coin=['btcusdt','ethusdt','ltcusdt','eosusdt','neousdt','etcusdt']
# kp_coin=['btcusdt','ethusdt','bchusdt','htusdt','xrpusdt','eosusdt']
kp_coin=['ethusdt']


# def api_getRealTimeDeal(kp='btcusdt'):
#     base_url=dom_url+'/market/trade?symbol='+kp
#     resHttpText = mHTTP.spyHTTP3(p_url=base_url)
#     if type(resHttpText) is int:
#         logger.debug('http异常')
#         return -1
#     rtn=json.loads(resHttpText,encoding='utf-8')
#     if rtn['status']<>u'ok':
#         logger.debug('http busi status 异常')
#         return -2
#     return rtn


def api_getRunData(mode='real'):

    try:
        if mode != 'real':
            insdb.sBtcClearDevOps()

        for i in range(len(kp_coin)):
            o = {}
            kp = kp_coin[i]
            o['kp'] = kp
            o['exn'] = 'HB'
            o['vol'] = 1
            if mode == 'real':
                time.sleep(10)
                rtn = insdb.sLoadKLineForPolicyLast(o)
            else:
                rtn = insdb.sLoadKLineForPolicyHis(o)


            for j in range(len(rtn)):
                real_rtn = rtn[j]
                '''
                场景一：
                价格在maXX下方0.3%
                '''
                logger.debug(str(j))
                if (real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30']<=gf_pol[0]['pol_threshold1']:

                    opsrtn = insdb.sBtcLoadLastOps(o)
                    # 进行买入判断
                    if len(opsrtn) > 0 and opsrtn[0]['direction'] == 'buy':
                        logger.debug(gf_pol[0]['pol_name']+'=> 已买入，无需再次买入')
                        continue

                    o['ddtime'] = mUtil.TimeStampNowStr()
                    o['direction'] = 'buy'
                    o['price'] = real_rtn['close']
                    o['profit'] = 0
                    o['pol_name'] = gf_pol[0]['pol_name']
                    o['rea'] = '[下方附近] 买入'
                    o['para'] = 'kutc='+str(real_rtn['kutc'])+',close='+str(real_rtn['close'])+',p_ma30='+str(real_rtn['p_ma30'])+',dlt='+str((real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30'])
                    logger.debug(gf_pol[0]['pol_name']+'=> '+o['rea']+','+str(real_rtn['close']))
                    insdb.sBtcInsertOps(o)

                # ag5_0=rtn[0]['angle_v_ma5']-rtn[1]['angle_v_ma5']
                # ag5_1=rtn[1]['angle_v_ma5']-rtn[2]['angle_v_ma5']
                # ag5_2=rtn[2]['angle_v_ma5']-rtn[3]['angle_v_ma5']

                '''
                场景二：
                应对单边突然上涨，对于上面场景的补充，最新价格在MA30上方0.5附件，三线一致开口
                '''
                # logger.debug(str(ag5_0))
                # logger.debug(str(ag5_1))
                # logger.debug(str(ag5_2))
                # logger.debug(str(ag5_0*ag5_1*ag5_2))
                # logger.debug(str(sum(ag5_0+ag5_1+ag5_2)))
                # logger.debug(str(sum(ag5_0+ag5_1+ag5_2)/3))

                cond1=real_rtn['angle_v_ma5']>0 and real_rtn['angle_v_ma30']>0
                cond2=real_rtn['angle_v_ma5']>real_rtn['angle_v_ma30']

                if (real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30']<=gf_pol[1]['pol_threshold1'] \
                        and real_rtn['close']>real_rtn['p_ma30'] and cond1 and cond2:

                    opsrtn = insdb.sBtcLoadLastOps(o)
                    #进行买入判断
                    if len(opsrtn)>0 and opsrtn[0]['direction'] == 'buy':
                        logger.debug(gf_pol[1]['pol_name']+'=> 已买入，无需再次买入')
                        continue

                    o['ddtime'] = mUtil.TimeStampNowStr()
                    o['direction'] = 'buy'
                    o['price'] = real_rtn['close']
                    o['profit'] = 0
                    o['pol_name']=gf_pol[1]['pol_name']
                    o['rea'] = '单边上扬'
                    o['para']=str(real_rtn['p_ma30'])+',ag5='+str(real_rtn['angle_v_ma5'])+',dlt='+str((real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30'])
                    logger.debug(gf_pol[1]['pol_name'] + '=> ' + o['rea'] + ',' + str(real_rtn['close']))
                    insdb.sBtcInsertOps(o)

                '''
                场景三：
                没有爬上ma30，反而朝下了
                超过0.5的比例，掉头向下了
                '''
                # if (real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30']<=-0.4 or \
                #     real_rtn['angle_v_ma5']<-30:
                #
                #     #进行卖出判断
                #     if len(opsrtn)==0 or opsrtn[0]['direction'] == 'sell':
                #         logger.debug('S3-已卖出,无需再次卖出')
                #         continue
                #     profit = real_rtn['close'] - opsrtn[0]['price']
                #     fee=(opsrtn[0]['price']+real_rtn['close'])*0.002
                #     o['ddtime'] = mUtil.TimeStampNowStr()
                #     o['direction'] = 'sell'
                #     o['price'] = real_rtn['close']
                #     # if profit>0:
                #     #     o['profit'] = profit-fee
                #     # else:
                #     o['profit'] = profit-fee
                #     o['pol_name']='p_ma30|'+kp
                #     o['rea_id'] = 'S3'
                #     o['rea'] = '再次下方[低于KP5=5,MA30] 卖出'
                #     o['para']=str(real_rtn['p_ma30'])+',ag5='+str(real_rtn['angle_v_ma5'])+',dlt='+str((real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30'])
                #     logger.debug(o['rea_id']+','+o['rea']+','+str(real_rtn['close']))
                #     insdb.sBtcInsertOps(o)

                '''
                场景四：
                必须强制盈利才肯抛出并且MA30上方调头，死多头
                '''

                # if len(opsrtn)>0:
                #     profit = real_rtn['close'] - opsrtn[0]['price']
                #     fee = (opsrtn[0]['price'] + real_rtn['close']) * 0.002
                #     real_profit=profit-fee

                # if ((real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30']>0.5 or
                #     real_profit*100/opsrtn[0]['price'] > 1) and real_rtn['angle_v_ma5'] < -20:

                cond1=real_rtn['angle_v_ma5']<0
                cond2=real_rtn['angle_v_ma5']<real_rtn['angle_v_ma30']
                cond3=(real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30']
                if cond1 and cond2 and cond3 > gf_pol[3]['pol_threshold1']:

                    opsrtn = insdb.sBtcLoadLastOps(o)
                    # 进行卖出判断
                    if len(opsrtn) == 0 or opsrtn[0]['direction'] == 'sell':
                        logger.debug(gf_pol[3]['pol_name']+'=> 已卖出，无需再次卖出')
                        continue

                    o['ddtime'] = mUtil.TimeStampNowStr()
                    o['direction'] = 'sell'
                    o['price'] = real_rtn['close']
                    profit = real_rtn['close'] - opsrtn[0]['price']
                    fee = (opsrtn[0]['price'] + real_rtn['close']) * 0.002
                    o['profit'] = profit - fee
                    o['pol_name'] = gf_pol[1]['pol_name']
                    o['rea'] = '卖出'
                    o['para'] = 'buy_price='+str(opsrtn[0]['price'])\
                                +'p_ma30='+str(real_rtn['p_ma30'])+',ag5='+str(real_rtn['angle_v_ma5'])\
                                +',dlt=' + str((real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30'])
                    logger.debug(gf_pol[3]['pol_name']+'=> ' + o['rea'] + ',' + str(real_rtn['close']))
                    insdb.sBtcInsertOps(o)

    except Exception, e:
        # logger.error('[ERR],' + e.message)
        logger.debug('[HS],' + traceback.format_exc())



# api_getRunData()
# logger.debug('等30秒')
# time.sleep(30)
# api_getRunData()
# logger.debug('结束')

print os.getenv('PYVV')
if os.getenv('PYVV') == 'dev':
    api_getRunData()
    sumRtn=insdb.sBtcSumDevProfit()
    logger.info(sumRtn[0].sumpft)

if os.getenv('PYVV')=='work':
    while True:
        api_getRunData(mode='train')
    # time.sleep(10)



# api_runpolicy()

# real price / 1min
# if os.getenv('PYVV')=='work' and sys.argv[1]=='1min':
    # for i in range(len(kp_coin)):
    # api_runpolicy(kp='btcusdt')
    # time.sleep(40)
    # api_runpolicy(kp='btcusdt')




