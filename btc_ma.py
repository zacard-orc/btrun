# -*- coding:utf-8 -*-
# btctrade
from __future__ import division


import os, json, thread, random, time, traceback, re, urllib,requests,datetime
from libs import mHTTP, mBusiLog, mUtil, mEnv, mDBA3
import numpy as np
import pandas as pd
# import xlwt
logger = mBusiLog.myLog(os.path.basename(__file__).split('.')[0] + '.log')

# ma求算
def get_ma_price(o_tunple):
    logger.debug('处理ma')
    for z in range(len(o_tunple)):

        #涨幅，上下引线
        o_tunple[z]['incr_pct']=round((o_tunple[z]['close']-o_tunple[z]['open'])*100/o_tunple[z]['open'],4)
        if o_tunple[z]['incr_pct']<0:
            o_tunple[z]['up_line_pct']=round((o_tunple[z]['high']-o_tunple[z]['open'])*100/o_tunple[z]['open'],4)
        else:
            o_tunple[z]['up_line_pct']=round((o_tunple[z]['high']-o_tunple[z]['close'])*100/o_tunple[z]['close'],4)

        # 前一天比较
        if z>0:
            o_tunple[z]['pre_incr_pct']= o_tunple[z-1]['incr_pct']
            o_tunple[z]['pre_up_line_pct']= o_tunple[z-1]['up_line_pct']

            #前一天是否包住后一天
            this_day_price=0
            pre_day_price=0
            if o_tunple[z]['incr_pct']<0:
                this_day_price=o_tunple[z]['open']
            else:
                this_day_price=o_tunple[z]['close']

            if o_tunple[z]['pre_incr_pct']<0:
                pre_day_price=o_tunple[z]['open']
            else:
                pre_day_price=o_tunple[z]['close']

            if pre_day_price>=this_day_price:
                o_tunple[z]['isWrapped']='Y'
            else:
                o_tunple[z]['isWrapped']='N'


        if z<4:
            continue

        sum_ma5=0
        sum_ma10=0
        for j in range(1,6):
            sum_ma5+=o_tunple[z-(6-j)+1]['close']

        for j in range(1,11):
            sum_ma10+=o_tunple[z-(11-j)+1]['close']

        o_tunple[z]['ma10']=round(sum_ma10/10,2)

    logger.debug('处理ma10拐点')
    for i in range(len(o_tunple)):
        # print fun_ma10_list[i]
        if i<5 or i==len(o_tunple)-1:
            continue

        o_tunple[i]['ma10_inflex_type'] = 'n/a'
        # #判断拐点
        if o_tunple[i]['ma10']>o_tunple[i-1]['ma10'] and o_tunple[i]['ma10']>o_tunple[i+1]['ma10']:
            o_tunple[i]['ma10_inflex_type']='up'
        if o_tunple[i]['ma10']<o_tunple[i-1]['ma10'] and o_tunple[i]['ma10']<o_tunple[i+1]['ma10']:
            o_tunple[i]['ma10_inflex_type']='bottom'

    return o_tunple

# ema计算
def get_EMA(d_list,N):
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

def get_ma_vol(his_list):
    logger.debug('处理ma vol')
    for z in range(len(his_list)):

        #MA5的量
        if z<4:
            continue
        sum_ma5=0
        for j in range(1,6):
            sum_ma5+=his_list[z-(6-j)+1]['vol']

        his_list[z]['ma5_vol']=round(sum_ma5/5,2)

        #5天前的MA量
        if z<4+5:
            continue

        his_list[z]['pre_fiveday_ma5_vol']=his_list[z-5]['ma5_vol']


    return his_list

# 主程序区域
sdb=mDBA3.A_SDB()

xtime=datetime.datetime.now()+datetime.timedelta(minutes=-5*1000)
sttime_flag=xtime.strftime('%Y%m%d%H%M%S')+'000'
o={}
o['sttime_flag']=sttime_flag
dbres=sdb.sbtc_loadk5(o)

his_list=get_ma_price(dbres)
his_list=get_EMA(his_list,12)
his_list=get_EMA(his_list,26)
his_list=get_DIFandDEA(his_list,9)
his_list=get_ma_vol(his_list)



logger.debug('构建PD')
# pds_ddhour=[] #用小时来索引
pds_idx=[] #用日期来索引
pds_macd_continuesday_plus=[]
pds_macd_continuesday_minus=[]
pds_macd_plus=[]
pds_macd=[]
pds_incr_pct=[]
pds_up_line_pct=[]
pds_pre_incr_pct=[]
pds_pre_up_line_pct=[]
pds_ma5_vol=[]
pds_pre_fiveday_ma5_vol=[]
pds_isWrapped=[]
pds_macd_inflex=[]

for i in range(len(his_list)):
    if i < 25+9+1: #25ema+9ema+1(prev protect none)
        continue
    pds_idx.append(his_list[i]['ddtime'])
    pds_macd_continuesday_minus.append(his_list[i]['macd_continuesday_minus'])
    pds_macd_continuesday_plus.append(his_list[i]['macd_continuesday_plus'])
    pds_macd_plus.append(his_list[i]['macd_plus'])
    pds_macd.append(his_list[i]['macd'])
    pds_incr_pct.append(his_list[i]['incr_pct'])
    pds_up_line_pct.append(his_list[i]['up_line_pct'])
    pds_pre_incr_pct.append(his_list[i]['pre_incr_pct'])
    pds_pre_up_line_pct.append(his_list[i]['pre_up_line_pct'])
    pds_ma5_vol.append(his_list[i]['ma5_vol'])
    pds_pre_fiveday_ma5_vol.append(his_list[i]['pre_fiveday_ma5_vol'])
    pds_isWrapped.append(his_list[i]['isWrapped'])
    pds_macd_inflex.append(his_list[i]['macd_inflex'])

df=pd.DataFrame({
    'macd_continuesday_plus':pds_macd_continuesday_plus,
    'macd_continuesday_minus': pds_macd_continuesday_minus,
    'macd_plus': pds_macd_plus,
    'macd': pds_macd,
    'incr_pct': pds_incr_pct,
    'up_line_pct': pds_up_line_pct,
    'pre_incr_pct': pds_pre_incr_pct,
    'pre_up_line_pct': pds_pre_up_line_pct,
    'ma5_vol': pds_ma5_vol,
    'pre_fiveday_ma5_vol': pds_pre_fiveday_ma5_vol,
    'isWrapped': pds_isWrapped,
    'macd_inflex':pds_macd_inflex
},index=pds_idx)

logger.debug('生成'+str(df.shape)+'矩阵PD')
logger.debug(str(df.dtypes))

df['macd_inflex']=df['macd_inflex'].map({'n/a':0,'up':1})
df['isWrapped']=df['isWrapped'].map({'N':0,'Y':1})
df['macd_plus']=df['macd_plus'].map({'N':0,'Y':1})


# df_corr=df[df['macd_inflex']==1].corr()
df_corr=df.corr()

# print df_corr
df_corr.to_excel('btc_corr.xls',sheet_name='Sheet1')
# df.to_excel('btc.xls',sheet_name='Sheet1')

logger.debug('写入Excel完毕')