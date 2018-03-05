# -*- coding:utf-8 -*-
# okex

from __future__ import division
import os,json,sys,time,xml,datetime,traceback,thread
import numpy as np
from libs import mHTTP, mBusiLog, mUtil, mEnv, mDBA2
from bs4 import  BeautifulSoup



insdb = mDBA2.A_SDB()
logger = mBusiLog.myLog(os.path.basename(__file__).split('.')[0] + '.log')
last_vol_delta=0

# base para
dom_url='https://www.okex.com'
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
kp_coin=[]
kp_coin_uniq={}
# kp_coin=['btcusdt','ethusdt','bchusdt','etcusdt','ltcusdt','eosusdt','xrpusdt','dashusdt',
#              'nasusdt','htusdt','hsrusdt','qtumusdt','iostusdt','neousdt','sntusdt',
#              'elaeth','chateth','thetaeth','mdseth','omgeth','storjusdt'
#     ,'ocneth','itceth','dgdeth','evxeth','btmeth']
kp_scale=3



def api_merged(kp='btc_usdt'):
    #买1卖1
    base_url=dom_url+'/market/detail/merged?symbol='+kp
    resHttpText = mHTTP.spyHTTP3(p_url=base_url)
    if type(resHttpText) is int:
        logger.debug('http异常')
        return -1
    rtn=json.loads(resHttpText,encoding='utf-8')
    if rtn['status']<>u'ok':
        logger.debug('http busi status 异常')
        return -2

    order_list = rtn['tick']
    oorder = {}
    oorder['b1_p'] = order_list['bid'][0]
    oorder['b1_a'] = order_list['bid'][1]
    oorder['s1_p'] = order_list['ask'][0]
    oorder['s1_a'] = order_list['ask'][1]
    return oorder




def api_kline(tp=5,kp='btc_usdt'):
    perd=''
    if tp==1:
        perd='1min'
    if tp==5:
        perd='5min'
    if tp==3600:
        perd='1day'

    base_url=dom_url+'/api/v1/kline.do?symbol='+kp+'&type=5min'

    resHttpText = mHTTP.spyHTTP3(p_url=base_url)
    if type(resHttpText) is int:
        logger.debug('http异常')
        return -1
    rtn=json.loads(resHttpText,encoding='utf-8')



    data=rtn

    ma_raw=[]
    his_high=[]
    his_low=[]
    for i in range(len(data)):
        # print data[i]
        o={}
        o['exn']='OKEx'
        o['tp']=str(tp)
        o['kp']=kp
        o['kutc']=mUtil.UTCtoSTDStamp(data[i][0]/1000)
        # o['amount']=data[i]['amount'] #成交量
        # o['count']=data[i]['count'] #笔数
        # o['vol']=data[i]['vol'] #成交额
        o['open']=float(data[i][1])
        o['high']=float(data[i][2])
        o['low']=float(data[i][3])
        o['close']=float(data[i][4])
        ma_raw.append(o)
        his_high.append(o['high'])
        his_low.append(o['low'])

    ma_raw.reverse()
    # print ma_raw
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
    rtn_o['exn']='OKEx'
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




def api_dealhis(kp='btc_usdt'):
    base_url=dom_url+'/api/v1/trades.do?symbol='+kp

    resHttpText = mHTTP.spyHTTP3(p_url=base_url,p_machinetype='h5')
    if type(resHttpText) is int:
        logger.debug('http异常')
        return -1

    rtn=json.loads(resHttpText)
    udata=rtn
    oa={}

    for j in range(len(udata)):
        ntime=mUtil.UTCtoSTDStamp(udata[j]['date'])[:16]

        if oa.has_key(ntime) is False:
            oa[ntime] = [0,0,0,0,0]  #买量，卖量，买卖比，买大单，卖大单

        accm=udata[j]['amount']*udata[j]['price']
        accm_cny=10000

        accm_base=p_base['usdt']
        accm=accm*accm_base



        if udata[j]['type']==u'buy':
            oa[ntime][0]+=udata[j]['amount']
            # if udata[j]['amount'] >= kp_coin_big[kp]:
            if accm>=accm_cny:
                oa[ntime][3] += udata[j]['amount']
        if udata[j]['type'] == u'sell':
            oa[ntime][1] += udata[j]['amount']
            if accm>=accm_cny:
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
        idb['exn']='OKEx'
        idb['kp']=kp
        idb['kutc']=m+':00'
        idb['buy_a']=oa[m][0]
        idb['sell_a']=oa[m][1]
        idb['sw']=oa[m][2]
        idb['buy_big_a']=oa[m][3]
        idb['sell_big_a']=oa[m][4]
        insdb.sBtcMarkAccInsert(idb)
    # dst = datetime.datetime.now() + datetime.timedelta(minutes=-1)
    # dst = dst.strftime('%Y-%m-%d %H:%M')
    # rtn_o={}
    # ##买量，卖量，买卖比，买大单，卖大单
    # rtn_o['ddtime']=dst
    # rtn_o['dtl_buy_a']=oa[dst][0]
    # rtn_o['dtl_sell_a']=oa[dst][1]
    # rtn_o['dtl_sw']=oa[dst][2]
    # rtn_o['dtl_buy_big_a']=oa[dst][3]
    # rtn_o['dtl_sell_big_a']=oa[dst][4]

    # return rtn_o




def api_commtxpair():
   a='<ul id="usdtCurrencyPair" class="list-main"><li data-symbol="btc_usdt" class="active"><i data-productid="20" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=btc_usdt" class="menu-spot-btc">BTC/USDT<em class="change-red">-1.50%</em><i class="menu-icon-margin">3X</i></a></li><li data-symbol="ltc_usdt"><i data-productid="25" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=ltc_usdt" class="menu-spot-btc">LTC/USDT<em class="change-red">-3.19%</em></a></li><li data-symbol="eth_usdt"><i data-productid="19" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=eth_usdt" class="menu-spot-btc">ETH/USDT<em class="change-red">-1.60%</em></a></li><li data-symbol="etc_usdt"><i data-productid="26" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=etc_usdt" class="menu-spot-btc">ETC/USDT<em class="change-green">+1.00%</em></a></li><li data-symbol="bch_usdt"><i data-productid="27" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=bch_usdt" class="menu-spot-btc">BCH/USDT<em class="change-red">-2.95%</em></a></li><li data-symbol="xrp_usdt"><i data-productid="47" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=xrp_usdt" class="menu-spot-btc">XRP/USDT<em class="change-red">-0.64%</em><i class="menu-icon-margin">3X</i></a></li><li data-symbol="xem_usdt"><i data-productid="231" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=xem_usdt" class="menu-spot-btc">XEM/USDT<em class="change-red">-5.18%</em></a></li><li data-symbol="xlm_usdt"><i data-productid="263" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=xlm_usdt" class="menu-spot-btc">XLM/USDT<em class="change-green">+8.64%</em></a></li><li data-symbol="iota_usdt"><i data-productid="53" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=iota_usdt" class="menu-spot-btc">IOTA/USDT<em class="change-red">-0.60%</em></a></li><li data-symbol="1st_usdt"><i data-productid="151" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=1st_usdt" class="menu-spot-btc">1ST/USDT<em class="change-red">-4.16%</em></a></li><li data-symbol="aac_usdt"><i data-productid="299" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=aac_usdt" class="menu-spot-btc">AAC/USDT<em class="change-red">-8.70%</em></a></li><li data-symbol="abt_usdt"><i data-productid="478" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=abt_usdt" class="menu-spot-btc">ABT/USDT<em class="change-red">-4.60%</em></a></li><li data-symbol="ace_usdt"><i data-productid="213" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=ace_usdt" class="menu-spot-btc">ACE/USDT<em class="change-red">-7.33%</em></a></li><li data-symbol="act_usdt"><i data-productid="65" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=act_usdt" class="menu-spot-btc">ACT/USDT<em class="change-red">-3.92%</em></a></li><li data-symbol="aidoc_usdt"><i data-productid="351" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=aidoc_usdt" class="menu-spot-btc">AIDOC/USDT<em class="change-red">-2.69%</em></a></li><li data-symbol="amm_usdt"><i data-productid="174" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=amm_usdt" class="menu-spot-btc">AMM/USDT<em class="change-green">+1.66%</em></a></li><li data-symbol="ark_usdt"><i data-productid="189" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=ark_usdt" class="menu-spot-btc">ARK/USDT<em class="change-red">-6.44%</em></a></li><li data-symbol="ast_usdt"><i data-productid="201" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=ast_usdt" class="menu-spot-btc">AST/USDT<em class="change-red">-1.59%</em></a></li><li data-symbol="atl_usdt"><i data-productid="387" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=atl_usdt" class="menu-spot-btc">ATL/USDT<em class="change-red">-8.23%</em></a></li><li data-symbol="auto_usdt"><i data-productid="487" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=auto_usdt" class="menu-spot-btc">AUTO/USDT<em class="change-red">-19.67%</em></a></li><li data-symbol="avt_usdt"><i data-productid="116" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=avt_usdt" class="menu-spot-btc">AVT/USDT<em class="change-red">-2.04%</em></a></li><li data-symbol="bcd_usdt"><i data-productid="68" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=bcd_usdt" class="menu-spot-btc">BCD/USDT<em class="change-red">-8.42%</em></a></li><li data-symbol="bec_usdt"><i data-productid="472" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=bec_usdt" class="menu-spot-btc">BEC/USDT<em class="change-green">+3.06%</em></a></li><li data-symbol="bkx_usdt"><i data-productid="481" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=bkx_usdt" class="menu-spot-btc">BKX/USDT<em class="change-red">-4.51%</em></a></li><li data-symbol="bnt_usdt"><i data-productid="156" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=bnt_usdt" class="menu-spot-btc">BNT/USDT<em class="change-red">-1.98%</em></a></li><li data-symbol="brd_usdt"><i data-productid="342" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=brd_usdt" class="menu-spot-btc">BRD/USDT<em class="change-green">+0.00%</em></a></li><li data-symbol="btg_usdt"><i data-productid="97" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=btg_usdt" class="menu-spot-btc">BTG/USDT<em class="change-red">-2.53%</em></a></li><li data-symbol="btm_usdt"><i data-productid="66" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=btm_usdt" class="menu-spot-btc">BTM/USDT<em class="change-green">+1.91%</em></a></li><li data-symbol="cag_usdt"><i data-productid="308" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=cag_usdt" class="menu-spot-btc">CAG/USDT<em class="change-green">+0.39%</em></a></li><li data-symbol="can_usdt"><i data-productid="411" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=can_usdt" class="menu-spot-btc">CAN/USDT<em class="change-green">+1.58%</em></a></li><li data-symbol="cbt_usdt"><i data-productid="463" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=cbt_usdt" class="menu-spot-btc">CBT/USDT<em class="change-red">-7.61%</em></a></li><li data-symbol="chat_usdt"><i data-productid="457" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=chat_usdt" class="menu-spot-btc">CHAT/USDT<em class="change-red">-3.32%</em></a></li><li data-symbol="cic_usdt"><i data-productid="451" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=cic_usdt" class="menu-spot-btc">CIC/USDT<em class="change-red">-5.93%</em></a></li><li data-symbol="cmt_usdt"><i data-productid="102" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=cmt_usdt" class="menu-spot-btc">CMT/USDT<em class="change-red">-2.56%</em></a></li><li data-symbol="ctr_usdt"><i data-productid="148" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=ctr_usdt" class="menu-spot-btc">CTR/USDT<em class="change-green">+0.38%</em></a></li><li data-symbol="cvc_usdt"><i data-productid="157" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=cvc_usdt" class="menu-spot-btc">CVC/USDT<em class="change-red">-3.89%</em></a></li><li data-symbol="dash_usdt"><i data-productid="46" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=dash_usdt" class="menu-spot-btc">DASH/USDT<em class="change-red">-1.88%</em></a></li><li data-symbol="dat_usdt"><i data-productid="180" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=dat_usdt" class="menu-spot-btc">DAT/USDT<em class="change-red">-1.11%</em></a></li><li data-symbol="dent_usdt"><i data-productid="436" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=dent_usdt" class="menu-spot-btc">DENT/USDT<em class="change-red">-12.27%</em></a></li><li data-symbol="dgb_usdt"><i data-productid="241" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=dgb_usdt" class="menu-spot-btc">DGB/USDT<em class="change-red">-7.14%</em></a></li><li data-symbol="dgd_usdt"><i data-productid="84" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=dgd_usdt" class="menu-spot-btc">DGD/USDT<em class="change-green">+10.42%</em></a></li><li data-symbol="dna_usdt"><i data-productid="314" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=dna_usdt" class="menu-spot-btc">DNA/USDT<em class="change-red">-8.34%</em></a></li><li data-symbol="dnt_usdt"><i data-productid="207" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=dnt_usdt" class="menu-spot-btc">DNT/USDT<em class="change-green">+3.85%</em></a></li><li data-symbol="dpy_usdt"><i data-productid="287" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=dpy_usdt" class="menu-spot-btc">DPY/USDT<em class="change-red">-1.12%</em></a></li><li data-symbol="edo_usdt"><i data-productid="115" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=edo_usdt" class="menu-spot-btc">EDO/USDT<em class="change-red">-9.45%</em></a></li><li data-symbol="elf_usdt"><i data-productid="198" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=elf_usdt" class="menu-spot-btc">ELF/USDT<em class="change-green">+5.78%</em></a></li><li data-symbol="eng_usdt"><i data-productid="249" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=eng_usdt" class="menu-spot-btc">ENG/USDT<em class="change-red">-6.78%</em></a></li><li data-symbol="eos_usdt"><i data-productid="59" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=eos_usdt" class="menu-spot-btc">EOS/USDT<em class="change-red">-3.39%</em></a></li><li data-symbol="evx_usdt"><i data-productid="219" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=evx_usdt" class="menu-spot-btc">EVX/USDT<em class="change-red">-2.07%</em></a></li><li data-symbol="fair_usdt"><i data-productid="302" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=fair_usdt" class="menu-spot-btc">FAIR/USDT<em class="change-red">-12.43%</em></a></li><li data-symbol="fun_usdt"><i data-productid="210" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=fun_usdt" class="menu-spot-btc">FUN/USDT<em class="change-red">-0.79%</em></a></li><li data-symbol="gas_usdt"><i data-productid="38" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=gas_usdt" class="menu-spot-btc">GAS/USDT<em class="change-red">-4.06%</em></a></li><li data-symbol="gnt_usdt"><i data-productid="85" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=gnt_usdt" class="menu-spot-btc">GNT/USDT<em class="change-green">+0.00%</em></a></li><li data-symbol="gnx_usdt"><i data-productid="183" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=gnx_usdt" class="menu-spot-btc">GNX/USDT<em class="change-green">+7.28%</em></a></li><li data-symbol="gsc_usdt"><i data-productid="490" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=gsc_usdt" class="menu-spot-btc">GSC/USDT<em class="change-green">+4.75%</em></a></li><li data-symbol="gtc_usdt"><i data-productid="484" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=gtc_usdt" class="menu-spot-btc">GTC/USDT<em class="change-red">-1.08%</em></a></li><li data-symbol="gto_usdt"><i data-productid="454" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=gto_usdt" class="menu-spot-btc">GTO/USDT<em class="change-red">-0.73%</em></a></li><li data-symbol="hmc_usdt"><i data-productid="442" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=hmc_usdt" class="menu-spot-btc">HMC/USDT<em class="change-red">-6.14%</em></a></li><li data-symbol="hot_usdt"><i data-productid="418" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=hot_usdt" class="menu-spot-btc">HOT/USDT<em class="change-green">+1.44%</em></a></li><li data-symbol="hsr_usdt"><i data-productid="39" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=hsr_usdt" class="menu-spot-btc">HSR/USDT<em class="change-red">-5.09%</em></a></li><li data-symbol="icn_usdt"><i data-productid="234" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=icn_usdt" class="menu-spot-btc">ICN/USDT<em class="change-red">-23.74%</em></a></li><li data-symbol="icx_usdt"><i data-productid="186" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=icx_usdt" class="menu-spot-btc">ICX/USDT<em class="change-red">-2.94%</em></a></li><li data-symbol="ins_usdt"><i data-productid="381" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=ins_usdt" class="menu-spot-btc">INS/USDT<em class="change-red">-5.54%</em></a></li><li data-symbol="insur_usdt"><i data-productid="460" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=insur_usdt" class="menu-spot-btc">INSUR/USDT<em class="change-green">+0.00%</em></a></li><li data-symbol="int_usdt"><i data-productid="357" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=int_usdt" class="menu-spot-btc">INT/USDT<em class="change-red">-0.23%</em></a></li><li data-symbol="iost_usdt"><i data-productid="369" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=iost_usdt" class="menu-spot-btc">IOST/USDT<em class="change-red">-1.73%</em></a></li><li data-symbol="ipc_usdt"><i data-productid="360" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=ipc_usdt" class="menu-spot-btc">IPC/USDT<em class="change-red">-11.53%</em></a></li><li data-symbol="itc_usdt"><i data-productid="103" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=itc_usdt" class="menu-spot-btc">ITC/USDT<em class="change-green">+5.92%</em></a></li><li data-symbol="kcash_usdt"><i data-productid="266" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=kcash_usdt" class="menu-spot-btc">KCASH/USDT<em class="change-green">+2.03%</em></a></li><li data-symbol="key_usdt"><i data-productid="420" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=key_usdt" class="menu-spot-btc">KEY/USDT<em class="change-green">+5.26%</em></a></li><li data-symbol="knc_usdt"><i data-productid="177" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=knc_usdt" class="menu-spot-btc">KNC/USDT<em class="change-green">+0.85%</em></a></li><li data-symbol="la_usdt"><i data-productid="355" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=la_usdt" class="menu-spot-btc">LA/USDT<em class="change-red">-3.30%</em></a></li><li data-symbol="lend_usdt"><i data-productid="313" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=lend_usdt" class="menu-spot-btc">LEND/USDT<em class="change-red">-9.09%</em></a></li><li data-symbol="lev_usdt"><i data-productid="393" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=lev_usdt" class="menu-spot-btc">LEV/USDT<em class="change-red">-3.37%</em></a></li><li data-symbol="light_usdt"><i data-productid="423" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=light_usdt" class="menu-spot-btc">LIGHT/USDT<em class="change-red">-8.33%</em></a></li><li data-symbol="link_usdt"><i data-productid="149" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=link_usdt" class="menu-spot-btc">LINK/USDT<em class="change-red">-4.21%</em></a></li><li data-symbol="lrc_usdt"><i data-productid="94" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=lrc_usdt" class="menu-spot-btc">LRC/USDT<em class="change-red">-0.34%</em></a></li><li data-symbol="mag_usdt"><i data-productid="333" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=mag_usdt" class="menu-spot-btc">MAG/USDT<em class="change-red">-3.49%</em></a></li><li data-symbol="mana_usdt"><i data-productid="165" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=mana_usdt" class="menu-spot-btc">MANA/USDT<em class="change-red">-2.13%</em></a></li><li data-symbol="mco_usdt"><i data-productid="96" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=mco_usdt" class="menu-spot-btc">MCO/USDT<em class="change-red">-4.89%</em></a></li><li data-symbol="mda_usdt"><i data-productid="222" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=mda_usdt" class="menu-spot-btc">MDA/USDT<em class="change-red">-6.43%</em></a></li><li data-symbol="mdt_usdt"><i data-productid="269" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=mdt_usdt" class="menu-spot-btc">MDT/USDT<em class="change-red">-1.74%</em></a></li><li data-symbol="mith_usdt"><i data-productid="475" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=mith_usdt" class="menu-spot-btc">MITH/USDT<em class="change-red">-10.68%</em></a></li><li data-symbol="mkr_usdt"><i data-productid="415" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=mkr_usdt" class="menu-spot-btc">MKR/USDT<em class="change-green">+5.42%</em></a></li><li data-symbol="mof_usdt"><i data-productid="378" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=mof_usdt" class="menu-spot-btc">MOF/USDT<em class="change-red">-0.15%</em></a></li><li data-symbol="mot_usdt"><i data-productid="327" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=mot_usdt" class="menu-spot-btc">MOT/USDT<em class="change-green">+7.03%</em></a></li><li data-symbol="mth_usdt"><i data-productid="225" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=mth_usdt" class="menu-spot-btc">MTH/USDT<em class="change-red">-2.30%</em></a></li><li data-symbol="mtl_usdt"><i data-productid="228" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=mtl_usdt" class="menu-spot-btc">MTL/USDT<em class="change-red">-2.05%</em></a></li><li data-symbol="nano_usdt"><i data-productid="448" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=nano_usdt" class="menu-spot-btc">NANO/USDT<em class="change-red">-4.71%</em></a></li><li data-symbol="nas_usdt"><i data-productid="272" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=nas_usdt" class="menu-spot-btc">NAS/USDT<em class="change-red">-0.84%</em></a></li><li data-symbol="neo_usdt"><i data-productid="37" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=neo_usdt" class="menu-spot-btc">NEO/USDT<em class="change-red">-4.64%</em></a></li><li data-symbol="ngc_usdt"><i data-productid="363" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=ngc_usdt" class="menu-spot-btc">NGC/USDT<em class="change-red">-7.46%</em></a></li><li data-symbol="nuls_usdt"><i data-productid="95" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=nuls_usdt" class="menu-spot-btc">NULS/USDT<em class="change-green">+15.94%</em></a></li><li data-symbol="oax_usdt"><i data-productid="245" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=oax_usdt" class="menu-spot-btc">OAX/USDT<em class="change-red">-12.73%</em></a></li><li data-symbol="of_usdt"><i data-productid="429" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=of_usdt" class="menu-spot-btc">OF/USDT<em class="change-green">+19.23%</em></a></li><li data-symbol="omg_usdt"><i data-productid="60" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=omg_usdt" class="menu-spot-btc">OMG/USDT<em class="change-red">-7.43%</em></a></li><li data-symbol="ost_usdt"><i data-productid="348" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=ost_usdt" class="menu-spot-btc">OST/USDT<em class="change-red">-9.09%</em></a></li><li data-symbol="pay_usdt"><i data-productid="83" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=pay_usdt" class="menu-spot-btc">PAY/USDT<em class="change-green">+4.09%</em></a></li><li data-symbol="poe_usdt"><i data-productid="372" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=poe_usdt" class="menu-spot-btc">POE/USDT<em class="change-green">+3.75%</em></a></li><li data-symbol="ppt_usdt"><i data-productid="243" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=ppt_usdt" class="menu-spot-btc">PPT/USDT<em class="change-red">-4.35%</em></a></li><li data-symbol="pra_usdt"><i data-productid="113" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=pra_usdt" class="menu-spot-btc">PRA/USDT<em class="change-red">-1.58%</em></a></li><li data-symbol="pst_usdt"><i data-productid="408" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=pst_usdt" class="menu-spot-btc">PST/USDT<em class="change-green">+5.33%</em></a></li><li data-symbol="qtum_usdt"><i data-productid="29" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=qtum_usdt" class="menu-spot-btc">QTUM/USDT<em class="change-red">-2.13%</em></a></li><li data-symbol="qun_usdt"><i data-productid="341" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=qun_usdt" class="menu-spot-btc">QUN/USDT<em class="change-red">-0.93%</em></a></li><li data-symbol="qvt_usdt"><i data-productid="195" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=qvt_usdt" class="menu-spot-btc">QVT/USDT<em class="change-red">-5.79%</em></a></li><li data-symbol="r_usdt"><i data-productid="466" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=r_usdt" class="menu-spot-btc">R/USDT<em class="change-red">-6.63%</em></a></li><li data-symbol="rcn_usdt"><i data-productid="251" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=rcn_usdt" class="menu-spot-btc">RCN/USDT<em class="change-red">-0.50%</em></a></li><li data-symbol="rct_usdt"><i data-productid="317" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=rct_usdt" class="menu-spot-btc">RCT/USDT<em class="change-red">-4.95%</em></a></li><li data-symbol="rdn_usdt"><i data-productid="257" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=rdn_usdt" class="menu-spot-btc">RDN/USDT<em class="change-red">-1.42%</em></a></li><li data-symbol="read_usdt"><i data-productid="290" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=read_usdt" class="menu-spot-btc">READ/USDT<em class="change-red">-3.96%</em></a></li><li data-symbol="ref_usdt"><i data-productid="402" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=ref_usdt" class="menu-spot-btc">REF/USDT<em class="change-green">+21.78%</em></a></li><li data-symbol="req_usdt"><i data-productid="247" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=req_usdt" class="menu-spot-btc">REQ/USDT<em class="change-red">-5.26%</em></a></li><li data-symbol="rfr_usdt"><i data-productid="493" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=rfr_usdt" class="menu-spot-btc">RFR/USDT<em class="change-red">-6.45%</em></a></li><li data-symbol="rnt_usdt"><i data-productid="275" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=rnt_usdt" class="menu-spot-btc">RNT/USDT<em class="change-red">-2.76%</em></a></li><li data-symbol="salt_usdt"><i data-productid="150" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=salt_usdt" class="menu-spot-btc">SALT/USDT<em class="change-red">-6.84%</em></a></li><li data-symbol="san_usdt"><i data-productid="114" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=san_usdt" class="menu-spot-btc">SAN/USDT<em class="change-red">-9.72%</em></a></li><li data-symbol="show_usdt"><i data-productid="321" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=show_usdt" class="menu-spot-btc">SHOW/USDT<em class="change-red">-3.57%</em></a></li><li data-symbol="smt_usdt"><i data-productid="300" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=smt_usdt" class="menu-spot-btc">SMT/USDT<em class="change-red">-0.83%</em></a></li><li data-symbol="snc_usdt"><i data-productid="405" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=snc_usdt" class="menu-spot-btc">SNC/USDT<em class="change-red">-5.31%</em></a></li><li data-symbol="sngls_usdt"><i data-productid="153" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=sngls_usdt" class="menu-spot-btc">SNGLS/USDT<em class="change-red">-6.29%</em></a></li><li data-symbol="snm_usdt"><i data-productid="154" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=snm_usdt" class="menu-spot-btc">SNM/USDT<em class="change-red">-0.43%</em></a></li><li data-symbol="snt_usdt"><i data-productid="74" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=snt_usdt" class="menu-spot-btc">SNT/USDT<em class="change-green">+1.43%</em></a></li><li data-symbol="soc_usdt"><i data-productid="432" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=soc_usdt" class="menu-spot-btc">SOC/USDT<em class="change-red">-5.84%</em></a></li><li data-symbol="spf_usdt"><i data-productid="398" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=spf_usdt" class="menu-spot-btc">SPF/USDT<em class="change-red">-7.37%</em></a></li><li data-symbol="ssc_usdt"><i data-productid="293" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=ssc_usdt" class="menu-spot-btc">SSC/USDT<em class="change-green">+2.73%</em></a></li><li data-symbol="stc_usdt"><i data-productid="399" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=stc_usdt" class="menu-spot-btc">STC/USDT<em class="change-red">-1.95%</em></a></li><li data-symbol="storj_usdt"><i data-productid="73" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=storj_usdt" class="menu-spot-btc">STORJ/USDT<em class="change-green">+10.47%</em></a></li><li data-symbol="sub_usdt"><i data-productid="204" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=sub_usdt" class="menu-spot-btc">SUB/USDT<em class="change-red">-8.33%</em></a></li><li data-symbol="swftc_usdt"><i data-productid="254" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=swftc_usdt" class="menu-spot-btc">SWFTC/USDT<em class="change-red">-6.40%</em></a></li><li data-symbol="tct_usdt"><i data-productid="384" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=tct_usdt" class="menu-spot-btc">TCT/USDT<em class="change-green">+8.68%</em></a></li><li data-symbol="theta_usdt"><i data-productid="391" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=theta_usdt" class="menu-spot-btc">THETA/USDT<em class="change-green">+4.42%</em></a></li><li data-symbol="tio_usdt"><i data-productid="366" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=tio_usdt" class="menu-spot-btc">TIO/USDT<em class="change-red">-8.17%</em></a></li><li data-symbol="tnb_usdt"><i data-productid="171" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=tnb_usdt" class="menu-spot-btc">TNB/USDT<em class="change-red">-5.65%</em></a></li><li data-symbol="topc_usdt"><i data-productid="337" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=topc_usdt" class="menu-spot-btc">TOPC/USDT<em class="change-red">-0.56%</em></a></li><li data-symbol="trio_usdt"><i data-productid="496" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=trio_usdt" class="menu-spot-btc">TRIO/USDT<em class="change-red">-10.61%</em></a></li><li data-symbol="true_usdt"><i data-productid="426" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=true_usdt" class="menu-spot-btc">TRUE/USDT<em class="change-red">-1.14%</em></a></li><li data-symbol="trx_usdt"><i data-productid="216" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=trx_usdt" class="menu-spot-btc">TRX/USDT<em class="change-red">-2.04%</em></a></li><li data-symbol="ubtc_usdt"><i data-productid="305" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=ubtc_usdt" class="menu-spot-btc">UBTC/USDT<em class="change-green">+13.72%</em></a></li><li data-symbol="uct_usdt"><i data-productid="469" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=uct_usdt" class="menu-spot-btc">UCT/USDT<em class="change-red">-4.02%</em></a></li><li data-symbol="ugc_usdt"><i data-productid="284" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=ugc_usdt" class="menu-spot-btc">UGC/USDT<em class="change-green">+2.55%</em></a></li><li data-symbol="ukg_usdt"><i data-productid="281" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=ukg_usdt" class="menu-spot-btc">UKG/USDT<em class="change-red">-0.77%</em></a></li><li data-symbol="utk_usdt"><i data-productid="330" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=utk_usdt" class="menu-spot-btc">UTK/USDT<em class="change-red">-0.36%</em></a></li><li data-symbol="vee_usdt"><i data-productid="168" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=vee_usdt" class="menu-spot-btc">VEE/USDT<em class="change-red">-4.05%</em></a></li><li data-symbol="vib_usdt"><i data-productid="324" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=vib_usdt" class="menu-spot-btc">VIB/USDT<em class="change-red">-0.90%</em></a></li><li data-symbol="viu_usdt"><i data-productid="346" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=viu_usdt" class="menu-spot-btc">VIU/USDT<em class="change-red">-1.92%</em></a></li><li data-symbol="wrc_usdt"><i data-productid="278" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=wrc_usdt" class="menu-spot-btc">WRC/USDT<em class="change-red">-7.30%</em></a></li><li data-symbol="wtc_usdt"><i data-productid="152" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=wtc_usdt" class="menu-spot-btc">WTC/USDT<em class="change-red">-7.06%</em></a></li><li data-symbol="xmr_usdt"><i data-productid="260" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=xmr_usdt" class="menu-spot-btc">XMR/USDT<em class="change-red">-2.41%</em></a></li><li data-symbol="xuc_usdt"><i data-productid="54" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=xuc_usdt" class="menu-spot-btc">XUC/USDT<em class="change-green">+14.62%</em></a></li><li data-symbol="yee_usdt"><i data-productid="377" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=yee_usdt" class="menu-spot-btc">YEE/USDT<em class="change-green">+1.48%</em></a></li><li data-symbol="yoyo_usdt"><i data-productid="192" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=yoyo_usdt" class="menu-spot-btc">YOYO/USDT<em class="change-green">+1.14%</em></a></li><li data-symbol="zec_usdt"><i data-productid="48" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=zec_usdt" class="menu-spot-btc">ZEC/USDT<em class="change-red">-3.11%</em></a></li><li data-symbol="zen_usdt"><i data-productid="439" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=zen_usdt" class="menu-spot-btc">ZEN/USDT<em class="change-red">-1.52%</em></a></li><li data-symbol="zip_usdt"><i data-productid="445" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=zip_usdt" class="menu-spot-btc">ZIP/USDT<em class="change-red">-11.11%</em></a></li><li data-symbol="zrx_usdt"><i data-productid="155" class="i-favorites "></i><a href="/spot/trade/index.do#symbol=zrx_usdt" class="menu-spot-btc">ZRX/USDT<em class="change-red">-3.59%</em></a></li></ul>'
   constct_html = BeautifulSoup(a, 'lxml')
   aa = constct_html.find_all('li')
   for i in range(len(aa)):
       kp_coin.append(aa[i].attrs['data-symbol'])

def runCollect():
    # sys.argv[1] == 'k1mindtl'
    if len(sys.argv)>1:
        num_split_kp=int(sys.argv[1])
        logger.debug('kp_split:'+sys.argv[1])
        for i in range(len(kp_coin)):
            logger.debug(kp_coin[i]+':'+str(i%kp_scale))
            if i % kp_scale == num_split_kp:
                try:
                    logger.debug(kp_coin[i])
                    ko1=api_kline(tp=5,kp=kp_coin[i])
                    # ko2=api_merged(kp_coin[i])
                    api_dealhis(kp_coin[i])
                    dictMerged1 = dict(ko1.items())
                    # dictMerged1 = dict(ko1.items() + ko2.items())

                    dictMerged1['kutc']=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:00')
                    insdb.sBtcMarkKline(dictMerged1)
                except Exception,e:
                    logger.debug('[OHS]' + traceback.format_exc())
    else:
        logger.warn('第二入参不存在')


def api_depth(kp='btc_usdt'):
    base_url = dom_url + '/api/v1/depth.do?symbol='+kp
    resHttpText = mHTTP.spyHTTP3(p_url=base_url)

    if type(resHttpText) is int:
        logger.debug('http异常')
        return -1

    rtn=json.loads(resHttpText)


    data=rtn

    #买盘
    bids_data=data['bids']
    bsum=0
    for i in range(len(bids_data)):
        bsum+=bids_data[i][1]

    # 卖盘
    asks_data = data['asks']
    asum = 0
    for i in range(len(asks_data)):
        asum += asks_data[i][1]
    return (bsum,asum)

api_commtxpair()
# api_depth()

# logger.debug(str(kp_coin))

#
# print len(kp_coin)
# for i in range(len(kp_coin)):
#     print kp_coin[i]
# time.sleep(111)

# print api_kline(tp=5,kp=kp_coin[0])
# api_dealhis()


logger.debug(os.getenv('PYVV'))
if os.getenv('PYVV')=='work_hy':
    while True:
        try:
            if int(sys.argv[1])<=2:
                logger.debug('标记为0的过滤USDT')

            runCollect()
            time.sleep(10)
        except Exception,e:
            logger.debug('[OHS]' + traceback.format_exc())
            # time.sleep(5)



logger.debug('结束')



