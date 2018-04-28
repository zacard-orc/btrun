# -*- coding:utf-8 -*-
# 2018.2.13
# 异动监控


from __future__ import division
import os,json,sys,time,xml,datetime,traceback,thread
import numpy as np
from libs import mHTTP, mBusiLog, mUtil, mEnv, mDBA2
from bs4 import  BeautifulSoup


insdb = mDBA2.A_SDB()
logger = mBusiLog.myLog(os.path.basename(__file__).split('.')[0] + '.log')

#设置幅度
ns=1.2

def loadDataSet(exn='OKEx'):
    o={}
    o['exn']=exn
    dbsets=insdb.sLoadKLineHis(o)
    kpl=[]
    for i in range(len(dbsets)):
        if i==0:
            kpl.append(dbsets[i])
            continue
        if dbsets[i]['kp']==kpl[-1]['kp']:
            #相同录入
            kpl.append(dbsets[i])
        else:
            #不相同，则对之前的KP做一次雷达运输
            n_kpl=len(kpl)
            n_delta=kpl[-1]['close']-kpl[0]['close']
            n_delat_pct=round(abs(n_delta)*100/kpl[0]['close'],2)
            logger.debug(mUtil.u8(kpl[0]['kp'])+','+str(n_delat_pct)+'%')
            #头尾涨幅
            if n_delat_pct>ns:
                #TODO 记录异动，msg_type,kp,exn,kutc,close,msg_value,msg_body
                o['msg_type']='异动'
                o['kp']=mUtil.u8(kpl[0]['kp'])
                o['kutc']=kpl[-1]['kutc'].strftime("%Y-%m-%d %H:%M:%S")
                o['close']=kpl[-1]['close']
                o['msg_value']=str(n_delat_pct)
                pct_desc='涨'
                o['msg_body']=o['kp']\
                              +',在'+o['exn']+'上行情'+o['msg_type']+'，价格为'+str(o['close'])\
                              +'，最近5分钟内'+pct_desc+'幅，达到'\
                              +str(n_delat_pct)+'%，请留意观察'
                if n_delta<0:
                    pct_desc='跌'
                    o['msg_value'] = str(-n_delat_pct)
                    o['msg_body']=o['kp']\
                                  +',在'+o['exn']+'上行情'+o['msg_type']+'，价格为'+str(o['close'])\
                                  +'，最近5分钟内'+pct_desc+'幅，达到'\
                                  +str(-n_delat_pct)+'%，请留意观察'


                insdb.sPushMsg(o)
                insdb.sPushMsgAnm(o)

            #连续开口
            if kpl[-1]['angle_v_ma5']>kpl[-1]['angle_v_ma30']*1.5 \
                and kpl[-1]['angle_v_ma30']>kpl[-1]['angle_v_ma60']*1.3 \
                and kpl[-1]['angle_v_ma5']>0 \
                and kpl[-1]['angle_v_ma30']>0 \
                and kpl[-1]['angle_v_ma60']>0:
                #开口向上
                o['msg_type']='开口向上'
                o['kp']=mUtil.u8(kpl[0]['kp'])
                o['kutc']=kpl[-1]['kutc'].strftime("%Y-%m-%d %H:%M:%S")
                o['close']=kpl[-1]['close']
                pct_desc='涨'
                o['msg_value']=str(n_delat_pct)
                o['msg_body']=o['kp']\
                              +',在'+o['exn']+'上行情'+o['msg_type']+'，价格为'+str(o['close'])\
                              +'，最近5分钟内'+pct_desc+'幅达到'\
                              +str(n_delat_pct)+'%，请留意观察'
                if n_delat_pct>ns:
                    insdb.sPushMsgAnm(o)

            if kpl[-1]['angle_v_ma5']<kpl[-1]['angle_v_ma30']*1.5 \
                and kpl[-1]['angle_v_ma30']<kpl[-1]['angle_v_ma60']*1.3 \
                and kpl[-1]['angle_v_ma5']<0 \
                and kpl[-1]['angle_v_ma30']<0 \
                and kpl[-1]['angle_v_ma60']<0:
                #开口向下
                o['msg_type']='开口向下'
                o['kp']=mUtil.u8(kpl[0]['kp'])
                o['kutc']=kpl[-1]['kutc'].strftime("%Y-%m-%d %H:%M:%S")
                o['close']=kpl[-1]['close']
                pct_desc='跌'
                o['msg_value']=str(n_delat_pct)
                o['msg_body']=o['kp']\
                              +',在'+o['exn']+'上行情'+o['msg_type']+'，价格为'+str(o['close'])\
                              +'，最近5分钟内'+pct_desc+'幅达到-'\
                              +str(n_delat_pct)+'%，请留意观察'
                if n_delat_pct>ns:
                    insdb.sPushMsgAnm(o)

            #急转弯
            if abs(kpl[-1]['angle_v_ma5'])>75:
                #开口向上
                o['msg_type']='急转弯'
                o['kp']=mUtil.u8(kpl[0]['kp'])
                o['kutc']=kpl[-1]['kutc'].strftime("%Y-%m-%d %H:%M:%S")
                o['close']=kpl[-1]['close']
                pct_desc='涨'
                if n_delta<0:
                    pct_desc='跌'
                o['msg_value']=str(n_delat_pct)
                o['msg_body']=o['kp']\
                              +',在'+o['exn']+'上行情'+o['msg_type']+'，价格为'+str(o['close'])\
                              +'，最近5分钟内'+pct_desc+'幅达到'\
                              +str(n_delat_pct)+'%，请留意观察'
                if n_delat_pct>ns:
                    insdb.sPushMsgAnm(o)

            #
            # #单调记录
            # if n_delat_pct<>0:
            #     n_delat_diff_ma5=[]
            #     n_delat_diff_ma30=[]
            #     n_delat_diff_ma60=[]
            #     for j in range(n_kpl):
            #         if j==0:
            #             continue
            #         n_delat_diff_ma5.append(kpl[j]['angle_v_ma5']-kpl[j-1]['angle_v_ma5'])
            #         n_delat_diff_ma30.append(kpl[j]['angle_v_ma30']-kpl[j-1]['angle_v_ma30'])
            #         n_delat_diff_ma60.append(kpl[j]['angle_v_ma60']-kpl[j-1]['angle_v_ma60'])
            #
            #     #单调上升
            #     n_ma5_up_status = False
            #     for j in range(len(n_delat_diff_ma5)):
            #         if n_delat_diff_ma5[j]>=0:
            #             n_ma5_up_status=True
            #         else:
            #             n_ma5_up_status=False
            #             break
            #     if n_ma5_up_status==True:
            #         #TODO 记录单调上升
            #         o['msg_type']='单调上升'
            #         o['kp']=mUtil.u8(kpl[0]['kp'])
            #         o['kutc']=kpl[-1]['kutc'].strftime("%Y-%m-%d %H:%M:%S")
            #         o['close']=kpl[-1]['close']
            #         pct_desc='涨'
            #         o['msg_value']=str(n_delat_pct)
            #         o['msg_body']=o['kp']\
            #                       +',在'+o['exn']+'交易所行情'+o['msg_type']+'，价格为'+str(o['close'])\
            #                       +'，最近5分钟内'+pct_desc+'幅达到'\
            #                       +str(n_delat_pct)+'%，请留意观察'
            #         insdb.sPushMsgAnm(o)
            #
            #     #单调下降
            #     n_ma5_down_status = False
            #     for j in range(len(n_delat_diff_ma5)):
            #         if n_delat_diff_ma5[j]<=0:
            #             n_ma5_down_status=True
            #         else:
            #             n_ma5_down_status=False
            #             break
            #     if n_ma5_down_status==True:
            #         #TODO 记录单调下降
            #         o['msg_type']='单调下降'
            #         o['kp']=mUtil.u8(kpl[0]['kp'])
            #         o['kutc']=kpl[-1]['kutc'].strftime("%Y-%m-%d %H:%M:%S")
            #         o['close']=kpl[-1]['close']
            #         pct_desc='跌'
            #         o['msg_value']=str(n_delat_pct)
            #         o['msg_body']=o['kp']\
            #                       +',在'+o['exn']+'交易所行情'+o['msg_type']+'，价格为'+str(o['close'])\
            #                       +'，最近5分钟内'+pct_desc+'幅达到-'\
            #                       +str(n_delat_pct)+'%，请留意观察'
            #         insdb.sPushMsgAnm(o)
            #


            kpl=[]
            kpl.append(dbsets[i])

    o['msg_type']='空'
    o['kp']=''
    o['kutc']=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    o['close']=0
    o['msg_value']='0'
    o['msg_body']='0'
    insdb.sPushMsgAnm(o)


# loadDataSet('OKEx')
# loadDataSet('HB')


if os.getenv('PYVV')=='work_hy':
    while True:
        try:
            loadDataSet('OKEx')
            loadDataSet('HB')
            loadDataSet('BN')
            loadDataSet('ZB')

        except Exception,e:
            logger.error(e.message)
            logger.debug('[OHS]' + traceback.format_exc())
            time.sleep(60)
        time.sleep(60)





