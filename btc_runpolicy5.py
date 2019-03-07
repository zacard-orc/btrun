# -*- coding:utf-8 -*-
'''
根据5分钟的MA30，MA60，略线上下位置来比对策
'''

from __future__ import division
from __future__ import unicode_literals

import os, json, sys, time, datetime, traceback
import numpy as np
from libs import mHTTP, mBusiLog, mUtil, mEnv, mDBA2, mEmail
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
          {'pol_name': 'pol_sell_ma30_ffset', 'pol_desc': '跌穿MA30', 'pol_threshold1': 0.3},
          {'pol_name': 'pol_sell_inflex', 'pol_desc': 'MA30上方出现拐点', 'pol_threshold1': 0.1}, ]

# kp_coin=['btcusdt','ethusdt','ltcusdt','eosusdt','neousdt','etcusdt']
# kp_coin=['btcusdt','ethusdt','bchusdt','htusdt','xrpusdt','eosusdt']
kp_coin = ['ethusdt', 'eosusdt', 'bchusdt', 'btcusdt', 'htusdt']


def api_getRunData(mode='real'):
    try:
        if mode != 'real':
            insdb.sBtcClearDevOps()

        msg_list = []
        for i in range(len(kp_coin)):
            o = {}
            kp = kp_coin[i]
            o['env'] = os.getenv('PYVV')
            o['kp'] = kp
            o['exn'] = 'HB'
            o['vol'] = 1
            if mode == 'real':
                rtn = insdb.sLoadKLineForPolicyLast(o)
            else:
                rtn = insdb.sLoadKLineForPolicyHis(o)

            for j in range(len(rtn)):
                real_rtn = rtn[j]
                # msg = kp + ',ma30 downarea,'+str(real_rtn['close'])
                # logger.debug(msg)
                # mEmail.sendEmail(msg, msg)
                '''
                场景一：
                价格在maXX下方0.3%
                '''
                logger.debug('判断数据，' + str(real_rtn['close']) + ',' + str(real_rtn['p_ma30']))
                cond1 = (real_rtn['close'] - real_rtn['p_ma30']) * 100 / real_rtn['p_ma30']
                cond2 = real_rtn['angle_v_ma5'] > 10
                if cond1 <= -1 and cond2:
                    msg = 'BBOT,' + kp + ',ma30下方,' + str(real_rtn['close'])+','+str(real_rtn['angle_v_ma5'])
                    logger.debug(msg)
                    msg_list.append(msg)
                    # msg_list.append(msg)

                    # mEmail.sendEmail(msg, msg)

                '''
                场景二：
                应对单边突然上涨，对于上面场景的补充，最新价格在MA30上方0.5附件，三线一致开口
                '''
                cond1 = real_rtn['angle_v_ma5'] > 0 and real_rtn['angle_v_ma30'] > 0
                cond2 = real_rtn['angle_v_ma5'] > real_rtn['angle_v_ma30']
                cond3 = real_rtn['angle_v_ma5'] >= 55

                if cond1 and cond2 and cond3:
                    msg = 'BBOT,' + kp + ',单边上涨,' + str(real_rtn['close']) + ',' + str(real_rtn['angle_v_ma5'])
                    logger.debug(msg)
                    msg_list.append(msg)
                    # mEmail.sendEmail(msg, msg)

                '''
                场景三：
                超过MA30多少以上就直接卖
                '''
                # cond1 = real_rtn['open'] > real_rtn['p_ma30']
                # cond2 = real_rtn['close'] < real_rtn['p_ma30']
                # if cond1 and cond2:



                '''
                场景四：
                M30上方出现拐点
                '''
                cond1 = real_rtn['angle_v_ma5'] < -20
                # cond2=real_rtn['angle_v_ma5']<real_rtn['angle_v_ma30']
                # cond3 = (real_rtn['close'] - real_rtn['p_ma30']) * 100 / real_rtn['p_ma30']
                cond4 = real_rtn['close'] > real_rtn['p_ma30']
                if cond1 and cond4:
                    msg = 'BBOT,' + kp + ',ma30 上方拐点,' + str(real_rtn['close'])
                    logger.debug(msg)
                    msg_list.append(msg)
                    #

        if len(msg_list)>0:
            sendMsg = u'\n'.join(msg_list)
            # print sendMsg
            # print type(sendMsg)
            # mEmail.sendEmail(sendMsg[:30], sendMsg)
            o={}
            o['type']='coin'
            o['msg']=sendMsg
            insdb.sBtcInsertPushMsg(o)
    except Exception, e:
        print traceback.format_exc()
        logger.debug('[HS],' + traceback.format_exc())


if os.getenv('PYVV') == 'dev':
    api_getRunData(mode='real')

if os.getenv('PYVV') == 'work':
    while True:
        api_getRunData(mode='real')
        logger.debug('等待下个监测点')
        time.sleep(60)
