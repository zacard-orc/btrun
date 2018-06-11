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
gf_pol_name='pol_ma30'
gf_tlz=0.999 #贪婪值，修正MA附近的凸起
gf_ma20defense=1.002


# kp_coin=['btcusdt','ethusdt','ltcusdt','eosusdt','neousdt','etcusdt']
kp_coin=['btcusdt','ethusdt','bchusdt','htusdt']


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

def api_getRunData():

    try:
        for i in range(len(kp_coin)):
            o = {}
            kp=kp_coin[i]
            o['kp']=kp
            o['exn']='HB'
            o['vol']=1
            rtn=insdb.sLoadKLineForPolicyBase(o)
            opsrtn = insdb.sBtcLoadLastOps(o)
            # print opsrtn
            if len(rtn)<=0:
                logger.debug('数据没有取到这次略过')
                continue

            real_rtn=rtn[0]
            pct_diff_ma30=(real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30']
            logger.debug(kp
                         +','+str(real_rtn['close'])
                         +','+str(round(real_rtn['p_ma30'],4))
                         +','+str(round(pct_diff_ma30,4))
                         +','+str(real_rtn['angle_v_ma5'])
                         +','+str(real_rtn['angle_v_ma30'])
                         )
            #p_ma30操作
            '''
            场景一：
            价格在ma30附近0.2%
            ma5开口向上0.2%并且开口向上，可以捡第一次，可以捡第二次
            '''
            if (real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30']<=-0.2 and \
               real_rtn['angle_v_ma5']>9:
                #进行买入判断
                if len(opsrtn)>0 and opsrtn[0]['direction']=='buy':
                    logger.debug('S1-已买入，无需再次买入')
                    continue

                o['ddtime'] = mUtil.TimeStampNowStr()
                o['direction'] = 'buy'
                o['price'] = real_rtn['close']
                o['profit'] = 0
                o['pol_name']='p_ma30|'+kp
                o['rea_id']='S1'
                if pct_diff_ma30>=0:
                    o['rea'] = '[MA30,0.2% 上方附近] 买入'
                else:
                    o['rea'] = '[MA30,0.2% 下方附近] 买入'
                o['para']=str(real_rtn['p_ma30'])+',ag5='+str(real_rtn['angle_v_ma5'])+',dlt='+str((real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30'])
                logger.debug(o['rea_id']+','+o['rea']+','+str(real_rtn['close']))
                insdb.sBtcInsertOps(o)

            ag5_0=rtn[0]['angle_v_ma5']-rtn[1]['angle_v_ma5']
            ag5_1=rtn[1]['angle_v_ma5']-rtn[2]['angle_v_ma5']
            ag5_2=rtn[2]['angle_v_ma5']-rtn[3]['angle_v_ma5']

            '''
            场景二：
            应对单边突然上涨，对于上面场景的补充，最新价格在MA30上方0.5附件，三线一致开口
            '''
            logger.debug(str(ag5_0))
            logger.debug(str(ag5_1))
            logger.debug(str(ag5_2))
            logger.debug(str(ag5_0*ag5_1*ag5_2))
            # logger.debug(str(sum(ag5_0+ag5_1+ag5_2)))
            # logger.debug(str(sum(ag5_0+ag5_1+ag5_2)/3))

            if (real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30']<=0.5 and \
                real_rtn['close']>real_rtn['p_ma30'] and ag5_0*ag5_1*ag5_2>0 and \
                (ag5_0+ag5_1+ag5_2)/3>4:

                #进行买入判断
                if len(opsrtn)>0 and opsrtn[0]['direction']=='buy':
                    logger.debug('S2-已买入，无需再次买入')
                    continue

                o['ddtime'] = mUtil.TimeStampNowStr()
                o['direction'] = 'buy'
                o['price'] = real_rtn['close']
                o['profit'] = 0
                o['pol_name']='p_ma30|'+kp
                o['rea_id'] = 'S2'
                o['rea'] = '单边上扬'
                o['para']=str(real_rtn['p_ma30'])+',ag5='+str(real_rtn['angle_v_ma5'])+',dlt='+str((real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30'])
                logger.debug(o['rea_id'] + ',' + o['rea'] + ',' + str(real_rtn['close']))
                insdb.sBtcInsertOps(o)


            '''
            场景三：
            没有爬上ma30，反而朝下了
            超过0.5的比例，掉头向下了
            '''
            # if (real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30']<=-0.2 or \
            #    (real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30']>0.5 and real_rtn['angle_v_ma5']<-30:
            #
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
            #     o['rea'] = '下方[低于KP5=5,MA30] 卖出'
            #     o['para']=str(real_rtn['p_ma30'])+',ag5='+str(real_rtn['angle_v_ma5'])+',dlt='+str((real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30'])
            #     logger.debug(o['rea_id']+','+o['rea']+','+str(real_rtn['close']))
            #     insdb.sBtcInsertOps(o)

            '''
            场景四：
            必须强制盈利才肯抛出并且MA30上方调头，死多头
            '''

            profit = real_rtn['close'] - opsrtn[0]['price']
            fee = (opsrtn[0]['price'] + real_rtn['close']) * 0.002
            real_profit=profit-fee

            if ((real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30']>0.5 or
                real_profit*100/opsrtn[0]['price'] > 1) and real_rtn['angle_v_ma5'] < -20:

                # 进行卖出判断
                if len(opsrtn) == 0 or opsrtn[0]['direction'] == 'sell':
                    logger.debug('S3-已卖出,无需再次卖出')
                    continue


                o['ddtime'] = mUtil.TimeStampNowStr()
                o['direction'] = 'sell'
                o['price'] = real_rtn['close']
                # if profit>0:
                #     o['profit'] = profit-fee
                # else:
                o['profit'] = profit - fee
                o['pol_name'] = 'p_ma30|' + kp
                o['rea_id'] = 'S4'
                o['rea'] = '强制锁定收益 卖出'
                o['para'] = 'buy_price='+str(opsrtn[0]['price'])\
                            +'p_ma30='+str(real_rtn['p_ma30'])+',ag5='+str(real_rtn['angle_v_ma5'])\
                            +',dlt=' + str((real_rtn['close']-real_rtn['p_ma30'])*100/real_rtn['p_ma30'])
                logger.debug(o['rea_id'] + ',' + o['rea'] + ',' + str(real_rtn['close']))
                insdb.sBtcInsertOps(o)

    except Exception, e:
        logger.error('[ERR],' + e.message)
        logger.debug('[HS],' + traceback.format_exc())



# api_getRunData()
# logger.debug('等30秒')
# time.sleep(30)
# api_getRunData()
# logger.debug('结束')


while True:
    api_getRunData()
    time.sleep(40)



# api_runpolicy()

# real price / 1min
# if os.getenv('PYVV')=='work' and sys.argv[1]=='1min':
    # for i in range(len(kp_coin)):
    # api_runpolicy(kp='btcusdt')
    # time.sleep(40)
    # api_runpolicy(kp='btcusdt')




