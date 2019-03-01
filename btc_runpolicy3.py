# -*- coding:utf-8 -*-
'''
根据5分钟的MA30，MA60，略线上下位置来比对策
'''

from __future__ import division
from __future__ import unicode_literals

import os, json, sys, time, datetime, traceback
import numpy as np
from libs import mHTTP, mBusiLog, mUtil, mEnv, mDBA2
from threading import Timer

insdb = mDBA2.A_SDB()
logger = mBusiLog.myLog(os.path.basename(__file__).split('.')[0] + '.log')
last_vol_delta = 0

# base para
dom_url = 'https://api.huobi.pro'
AccessKeyId = '08f4bb11-da3cb5d9-81292c66-f7372'
SignatureMethod = 'HmacSHA256'
SignatureVersion = '2'

# policy参数
# gf_pol_name='pol_ma30'
# gf_tlz=0.999 #贪婪值，修正MA附近的凸起
# gf_ma20defense=1.002

gf_pol = [{'pol_name': 'pol_buy_ma30_offset', 'pol_desc': 'ma30下方买入', 'pol_threshold1': -0.3},
          {'pol_name': 'pol_buy_rushup', 'pol_desc': '快速上涨开口向上', 'pol_threshold1': 0.5},
          {'pol_name': 'pol_sell_ma30_ffset', 'pol_desc': '跌穿MA30','pol_threshold1': 0.3},
          {'pol_name': 'pol_sell_inflex', 'pol_desc': 'MA30上方出现拐点','pol_threshold1': 0.1}, ]

# kp_coin=['btcusdt','ethusdt','ltcusdt','eosusdt','neousdt','etcusdt']
# kp_coin=['btcusdt','ethusdt','bchusdt','htusdt','xrpusdt','eosusdt']
kp_coin = ['ethusdt']


def api_getRunData(mode='real'):
    try:
        if mode != 'real':
            insdb.sBtcClearDevOps()

        for i in range(len(kp_coin)):
            o = {}
            kp = kp_coin[i]
            o['env'] = os.getenv('PYVV')
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
                cond1 = (real_rtn['close'] - real_rtn['p_ma30']) * 100 / real_rtn['p_ma30']
                cond2 = real_rtn['angle_v_ma5'] > 5
                if cond1 <= -1 and cond2:

                    opsrtn = insdb.sBtcLoadLastOps(o)
                    # 进行买入判断
                    if len(opsrtn) > 0 and opsrtn[0]['direction'] == 'buy':
                        logger.debug(gf_pol[0]['pol_name'] + '=> 已买入，无需再次买入')
                        continue

                    o['ddtime'] = mUtil.TimeStampNowStr()
                    o['ddtime_snap'] = real_rtn['kutc'].strftime('%Y-%m-%d %H:%M')
                    o['direction'] = 'buy'
                    o['price'] = real_rtn['close']
                    o['profit'] = 0
                    o['pol_name'] = gf_pol[0]['pol_name']
                    o['rea'] = '[下方附近] 买入'
                    o['para'] = 'kutc=' + str(real_rtn['kutc']) + ',close=' + str(real_rtn['close']) + ',p_ma30=' + str(
                        real_rtn['p_ma30']) + ',dlt=' + str(
                        (real_rtn['close'] - real_rtn['p_ma30']) * 100 / real_rtn['p_ma30'])
                    logger.debug(gf_pol[0]['pol_name'] + '=> ' + o['rea'] + ',' + str(real_rtn['close']))
                    insdb.sBtcInsertOps(o)

                # ag5_0=rtn[0]['angle_v_ma5']-rtn[1]['angle_v_ma5']
                # ag5_1=rtn[1]['angle_v_ma5']-rtn[2]['angle_v_ma5']
                # ag5_2=rtn[2]['angle_v_ma5']-rtn[3]['angle_v_ma5']

                '''
                场景二：
                应对单边突然上涨，对于上面场景的补充，最新价格在MA30上方0.5附件，三线一致开口
                '''
                cond1 = real_rtn['angle_v_ma5'] > 0 and real_rtn['angle_v_ma30'] > 0
                cond2 = real_rtn['angle_v_ma5'] > real_rtn['angle_v_ma30']
                cond3 = real_rtn['angle_v_ma5'] >= 45

                if cond1 and cond2 and cond3:
                    opsrtn = insdb.sBtcLoadLastOps(o)
                    # 进行买入判断
                    if len(opsrtn) > 0 and opsrtn[0]['direction'] == 'buy':
                        logger.debug(gf_pol[1]['pol_name'] + '=> 已买入，无需再次买入')
                        continue

                    o['ddtime'] = mUtil.TimeStampNowStr()
                    o['ddtime_snap'] = real_rtn['kutc'].strftime('%Y-%m-%d %H:%M')
                    o['direction'] = 'buy'
                    o['price'] = real_rtn['close']
                    o['profit'] = 0
                    o['pol_name'] = gf_pol[1]['pol_name']
                    o['rea'] = '单边上扬'
                    o['para'] = str(real_rtn['p_ma30']) + ',ag5=' + str(real_rtn['angle_v_ma5']) + ',dlt=' + str(
                        (real_rtn['close'] - real_rtn['p_ma30']) * 100 / real_rtn['p_ma30'])
                    logger.debug(gf_pol[1]['pol_name'] + '=> ' + o['rea'] + ',' + str(real_rtn['close']))
                    insdb.sBtcInsertOps(o)

                '''
                场景三：
                超过MA30多少以上就直接卖
                '''
                cond1 = real_rtn['open'] > real_rtn['p_ma30']
                cond2 = real_rtn['close'] < real_rtn['p_ma30']
                if cond1 and cond2:

                    opsrtn = insdb.sBtcLoadLastOps(o)
                    # 进行卖出判断
                    if len(opsrtn) == 0 or opsrtn[0]['direction'] == 'sell':
                        logger.debug(gf_pol[2]['pol_name'] + '=> 已卖出，无需再次卖出')
                        continue

                    o['ddtime'] = mUtil.TimeStampNowStr()
                    o['ddtime_snap'] = real_rtn['kutc'].strftime('%Y-%m-%d %H:%M')
                    o['direction'] = 'sell'
                    o['price'] = real_rtn['close']
                    profit = real_rtn['close'] - opsrtn[0]['price']
                    fee = (opsrtn[0]['price'] + real_rtn['close']) * 0.002
                    o['profit'] = profit - fee
                    o['pol_name'] = gf_pol[2]['pol_name']
                    o['rea'] = '跌穿MA30'
                    o['para'] = 'buy_price=' + str(opsrtn[0]['price']) + 'p_ma30=' + str(
                        real_rtn['p_ma30']) + ',ag5=' + str(real_rtn['angle_v_ma5']) + ',dlt=' + str(
                        (real_rtn['close'] - real_rtn['p_ma30']) * 100 / real_rtn['p_ma30'])
                    logger.debug(gf_pol[2]['pol_name'] + '=> ' + o['rea'] + ',' + str(real_rtn['close']))
                    insdb.sBtcInsertOps(o)

                '''
                场景四：
                M30上方出现拐点
                '''
                cond1 = real_rtn['angle_v_ma5'] < -20
                # cond2=real_rtn['angle_v_ma5']<real_rtn['angle_v_ma30']
                # cond3 = (real_rtn['close'] - real_rtn['p_ma30']) * 100 / real_rtn['p_ma30']
                cond4 = real_rtn['close'] > real_rtn['p_ma30']
                if cond1 and cond4 :

                    opsrtn = insdb.sBtcLoadLastOps(o)
                    # 进行卖出判断
                    if len(opsrtn) == 0 or opsrtn[0]['direction'] == 'sell':
                        logger.debug(gf_pol[3]['pol_name'] + '=> 已卖出，无需再次卖出')
                        continue

                    o['ddtime'] = mUtil.TimeStampNowStr()
                    o['ddtime_snap'] = real_rtn['kutc'].strftime('%Y-%m-%d %H:%M')
                    o['direction'] = 'sell'
                    o['price'] = real_rtn['close']
                    profit = real_rtn['close'] - opsrtn[0]['price']
                    fee = (opsrtn[0]['price'] + real_rtn['close']) * 0.002
                    o['profit'] = profit - fee
                    o['pol_name'] = gf_pol[3]['pol_name']
                    o['rea'] = 'MA30上方拐点'
                    o['para'] = 'buy_price=' + str(opsrtn[0]['price']) + 'p_ma30=' + str(
                        real_rtn['p_ma30']) + ',ag5=' + str(real_rtn['angle_v_ma5']) + ',dlt=' + str(
                        (real_rtn['close'] - real_rtn['p_ma30']) * 100 / real_rtn['p_ma30'])
                    logger.debug(gf_pol[3]['pol_name'] + '=> ' + o['rea'] + ',' + str(real_rtn['close']))
                    insdb.sBtcInsertOps(o)

    except Exception, e:
        # logger.error('[ERR],' + e.message)
        logger.debug('[HS],' + traceback.format_exc())




print os.getenv('PYVV')
if os.getenv('PYVV') == 'dev':
    api_getRunData(mode='train')
    sumRtn = insdb.sBtcSumDevProfit()
    logger.info(sumRtn[0]['sumpft'])

if os.getenv('PYVV') == 'work':
    while True:
        api_getRunData(mode='train')



        # api_runpolicy()

        # real price / 1min
        # if os.getenv('PYVV')=='work' and sys.argv[1]=='1min':
        # for i in range(len(kp_coin)):
        # api_runpolicy(kp='btcusdt')
        # time.sleep(40)
        # api_runpolicy(kp='btcusdt')
