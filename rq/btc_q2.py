# -*- coding:utf-8 -*-
# 火币 米匡-K线

from __future__ import division
import os,time
import numpy as np
from libs import mHTTP, mBusiLog, mUtil, mEnv,mDBA3
import pandas as pd



insdb = mDBA3.A_SDB()
logger = mBusiLog.myLog(os.path.basename(__file__).split('.')[0] + '.log')

kp_coin=['btcusdt','bchusdt','ethusdt','neousdt','eosusdt',
         'qtumusdt','etcusdt','ltcusdt','dashusdt','abteth',
         'xrpusdt','itceth','btmeth','omgeth','storjusdt','iostusdt']


def get_EMA(d_list,N): #升序入参
    logger.debug('处理周期的ema_'+str(N))

    for i in range(len(d_list)):
        if i<25:
            continue

        ema_list=np.zeros(N)
        for z in range(N):
            day_id=i-(N-z)+1  #方便从1开始计数,从第前N天开始计算

            if z==0:
                ema_list[z]=(2*d_list[day_id]['close'])/2
            else:
                ema_list[z]=(2*d_list[day_id]['close']+(z+1-1)*ema_list[z-1])/(z+1+1)
        d_list[i]['ema_'+str(N)]=round(ema_list[-1],2)

    return d_list

for i in range(len(kp_coin)):
    o={}
    o['kp']=kp_coin[i]
    o['pertime']=3 #小时
    rtn=insdb.sLoadKLineBasic(o)
    #开始数据清洗
    # 引线处理
    pdl_lead_up = []  # 上引线
    pdl_lead_down = []  # 下引线
    pdl_ma30_delta =[]  #ma30差值
    pdl_cross_530=[]  #5、30交叉
    pdl_cross_3060=[]  #30、60交叉
    pdl_ag5=[]
    pdl_ag30=[]
    pdl_ag60=[]
    pdl_count=[]
    pdl_pcts=[]
    pdl_dk=[]
    pdl_dk_big=[]

    pdl_class=[]   #分类,0=默认，1=顶，2=底

    '''
    上引线比例
    下引线比例
    ma30 delta
    ma5 > ma30
    ma30 > ma60
    角度ma5
    角度ma30
    角度ma60
    count成交次数
    pcts水位线
    多空力量
    多空大单力量
    '''

    for j in range(len(rtn)):

        #基础值传递
        pdl_ag5.append(rtn[j]['angle_v_ma5'])
        pdl_ag30.append(rtn[j]['angle_v_ma30'])
        pdl_ag60.append(rtn[j]['angle_v_ma60'])
        pdl_count.append(rtn[j]['count'])
        pdl_pcts.append(rtn[j]['pcts'])
        pdl_dk.append(rtn[j]['dk_r'])
        pdl_dk_big.append(rtn[j]['dk_big_r'])

        #蜡烛
        candle_body=abs(rtn[j]['open']-rtn[j]['close'])
        candle_max=max(rtn[j]['open'],rtn[j]['close'])
        candle_min=min(rtn[j]['open'],rtn[j]['close'])

        pdl_lead_up.append(round((rtn[j]['high']-candle_max)/candle_body,2))
        pdl_lead_down.append(round((candle_min-rtn[j]['low'])/candle_body,2))

        #ma30差值
        pdl_ma30_delta.append(rtn[j]['close']-rtn[j]['p_ma30'])

        #ma5/30/60位置比较
        if rtn[j]['p_ma5']>rtn[j]['p_ma30']:
            pdl_cross_530.append(1)
        else:
            pdl_cross_530.append(0)

        if rtn[j]['p_ma30']>rtn[j]['p_ma60']:
            pdl_cross_3060.append(1)
        else:
            pdl_cross_3060.append(0)

        if j<=2 or j>=len(rtn)-3:
            pdl_class.append(0)
            continue


        #判断顶点
        rzrange=3
        flag_high=True
        flag_low=True

        for rz in range(-rzrange,rzrange+1):
            if rz==0:
                continue
            if rtn[j]['high']>rtn[j+rz]['high']:
                flag_high = True
            else:
                flag_high = False
                break

        for rz in range(-rzrange,rzrange+1):
            if rz==0:
                continue
            if rtn[j]['low']<rtn[j+rz]['low']:
                flag_low = True
            else:
                flag_low = False
                break

        if flag_high==True:
            pdl_class.append(1)
            logger.debug(rtn[j]['kutc'].strftime("%Y-%m-%d %H:%M") + ' 顶点')
        if flag_low==True:
            pdl_class.append(2)
            logger.debug(rtn[j]['kutc'].strftime("%Y-%m-%d %H:%M") + ' 低点')



        '''
        上引线比例
        下引线比例
        ma30 delta
        ma5 > ma30
        ma30 > ma60
        角度ma5
        角度ma30
        角度ma60
        count成交次数
        pcts水位线
        多空力量
        多空大单力量
        macd 
        '''


    time.sleep(11)