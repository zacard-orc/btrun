# -*- coding:utf-8 -*-
# 火币 米匡-K线

from __future__ import division
import os,time,traceback
import numpy as np
from libs import mHTTP, mBusiLog, mUtil, mEnv,mDBA3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn import metrics
from sklearn import svm

import seaborn as sns
import matplotlib.pyplot as plt


insdb = mDBA3.A_SDB()
logger = mBusiLog.myLog(os.path.basename(__file__).split('.')[0] + '.log')

kp_coin=['btcusdt','ethusdt','neousdt','eosusdt',
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
        if d_list[i]['macd']>0:
            d_list[i]['macd_plus']='Y'
        else:
            d_list[i]['macd_plus']='N'


    logger.debug('处理MACD拐点')

    #连续MACD单调天数
    last_bottom_inflex_info = None
    last_up_inflex_info = None
    continuesday_plus_num=0
    continuesday_minus_num=0
    for i in range(len(d_list)):

        if i < 25 + 9 + 1:
            continue

        if d_list[i]['macd']>=d_list[i-1]['macd']: #上涨
            continuesday_plus_num+=1
            d_list[i]['macd_continuesday_plus'] = continuesday_plus_num
            d_list[i]['macd_continuesday_minus'] = 0

        else:
            continuesday_minus_num+=1
            d_list[i]['macd_continuesday_plus'] = 0
            d_list[i]['macd_continuesday_minus'] = continuesday_minus_num

        d_list[i]['macd_inflex']='n/a'
        if i < 25+9+1 or i==len(d_list)-1:
            continue


        d_list[i]['macd_inflex']='n/a'
        if d_list[i]['macd']>d_list[i-1]['macd'] and d_list[i]['macd']>d_list[i+1]['macd'] and d_list[i]['macd']>0:
            d_list[i]['macd_inflex']='up'
            continuesday_plus_num=0

        if d_list[i]['macd']<d_list[i-1]['macd'] and d_list[i]['macd']<d_list[i+1]['macd'] and d_list[i]['macd']<0:
            d_list[i]['macd_inflex']='n/a'
            continuesday_minus_num=0

    return d_list


try:
    for i in range(len(kp_coin)):
        o={}
        o['kp']=kp_coin[i]
        o['pertime']=999 #小时
        rtn=insdb.sLoadKLineBasic(o)

        rtn=get_EMA(rtn,12)
        rtn=get_EMA(rtn,26)
        rtn=get_DIFandDEA(rtn,9)

        #开始数据清洗
        pdl_idx=[] #标题索引
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
        pdl_macd=[]
        pdl_vol=[]
        pdl_close=[]

        pdl_class=[]   #分类,0=默认，1=顶，2=底


        for j in range(len(rtn)):

            if j<25+9:
                continue

            #基础值传递
            pdl_idx.append(rtn[j]['kutc'].strftime("%d %H:%M"))
            pdl_ag5.append(rtn[j]['angle_v_ma5'])
            pdl_ag30.append(rtn[j]['angle_v_ma30'])
            pdl_ag60.append(rtn[j]['angle_v_ma60'])
            pdl_count.append(rtn[j]['count'])
            pdl_pcts.append(rtn[j]['pcts'])
            pdl_dk.append(rtn[j]['dk_r'])
            pdl_vol.append(rtn[j]['vol'])
            pdl_dk_big.append(rtn[j]['dk_big_r'])
            pdl_macd.append(rtn[j]['macd'])
            pdl_close.append(rtn[j]['close'])

            #蜡烛
            candle_body=abs(rtn[j]['open']-rtn[j]['close'])
            candle_max=max(rtn[j]['open'],rtn[j]['close'])
            candle_min=min(rtn[j]['open'],rtn[j]['close'])

            if candle_body==0:
                candle_body=1


            pdl_lead_up.append(round((rtn[j]['high']-candle_max)/candle_body,2))
            pdl_lead_down.append(round((candle_min-rtn[j]['low'])/candle_body,2))

            #ma30差值
            pdl_ma30_delta.append(round((rtn[j]['close']-rtn[j]['p_ma30'])/rtn[j]['p_ma30'],2))
            pdl_class.append(0)

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
                pdl_class[-1]=1
                logger.debug(rtn[j]['kutc'].strftime("%Y-%m-%d %H:%M") + ' 顶点')
            if flag_low==True:
                pdl_class[-1]=2
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

        #Pandas登场
        df=pd.DataFrame({
            'lead_up':pdl_lead_up,
            'lead_down':pdl_lead_down,
            # 'ma30_delta':pdl_ma30_delta,
            'cross_530':pdl_cross_530,
            # 'cross_3060':pdl_cross_3060,
            'ma30_delta':pdl_ma30_delta,
            'ag5':pdl_ag5,
            'ag30':pdl_ag30,
            # 'ag60':pdl_ag60,
            # 'count':pdl_count,
            # 'pcts':pdl_pcts,
            'dk':pdl_dk,
            # 'dk_big':pdl_dk_big,
            'macd':pdl_macd,
            'class':pdl_class
        },index=pdl_idx)

        logger.debug('生成' + str(df.shape) + '矩阵PD')
        logger.debug(str(df.dtypes))
        logger.debug(str(df.describe()))
        # logger.debug(str(df.info))

        all_label = df['class'].values
        df_train = df.drop(['class'], axis=1)
        all_train = df_train.values

        X_train, X_test, y_train, y_test = train_test_split(all_train, all_label, test_size=0.2, random_state=1)


        y_pred=OneVsRestClassifier(LinearSVC(random_state=0)).fit(X_train, y_train).predict(X_test)
        logger.debug('train nums='+str(len(X_train)))
        logger.debug(str(y_test))
        logger.debug(str(y_pred))

        #计算分类精确指数
        met_total=len(y_test)
        met_true=0
        for z in range(met_total):
            if y_test[z]==y_pred[z]:
                met_true+=1

        logger.debug('AUC:'+str(round(met_true*100/met_total,4)))




        time.sleep(1111)
except Exception,e:
    logger.debug('[OHS]' + traceback.format_exc())





