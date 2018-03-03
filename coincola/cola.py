# coding: utf-8
#     PURPOSE:   携程教程7.4
#     VERSION:   0.0.1
#     AUTHOR:    Lin Leiying
#     MODIFIED:  2017/12/25 08:00

'''
drop table if exists wbtc_seat_dtl;
create table wbtc_seat_dtl(
type varchar(64),
query_id integer,
uid varchar(64),
pay_type varchar(64),
pay_range varchar(64),
pay_price double,
updateAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) engine=INNODB DEFAULT CHARSET=utf8mb4;
'''
import sys
sys.path.append("../")
import requests,os,time,thread,traceback
from bs4 import  BeautifulSoup
from libs import mBusiLog,mDBA4,mEnv,mUtil
# import jieba.analyse

logger = mBusiLog.myLog(os.path.basename(__file__).split('.')[0] + '.log')


#URL配置
out_u={
    'btc_buy':'https://www.coincola.com/buy/BTC?country_code=CN',
    'btc_sell':'https://www.coincola.com/sell/BTC?country_code=CN',
    'etc_buy':'https://www.coincola.com/buy/ETH?country_code=CN',
    'etc_sell':'https://www.coincola.com/sell/ETH?country_code=CN',
    'ltc_buy':'https://www.coincola.com/buy/LTC?country_code=CN',
    'ltc_sell':'https://www.coincola.com/sell/LTC?country_code=CN'
}

def caiji(ins_db,k,u):
    while True:
        gb_query_id=int(time.time())
        logger.debug('[Thread:'+k+'],'+k)
        myheaders = {'User-Agent': mEnv.env_ua['macpc'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip',
            'Accept-Language': 'zh-CN',
            'remoteAddress': mUtil.genFateIP(),
            'X-Forwarded-For': mUtil.genFateIP(),
            'X-Real-IP': mUtil.genFateIP(),
            'Referer': 'www.ctrip.com',
            'Cookie': mUtil.getMyCookie()
        }
        try:
            r=requests.get(u,verify=False,headers=myheaders)
            constct_html = BeautifulSoup(r.text, 'html.parser')

            tb=constct_html.find('table',class_='table buy')
            tb=tb.tbody
            trs=tb.find_all('tr')
            for i in range(len(trs)):
                tds=trs[i].find_all('td')
                # print tds[0]
                as1=tds[0].find_all('a')

                '''
                create table wbtc_seat_dtl(
                type varchar(64),
                query_id integer,
                uid varchar(64),
                pay_type varchar(64),
                pay_range varchar(64),
                pay_price double,
                updateAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) engine=INNODB DEFAULT CHARSET=utf8mb4;
                '''
                o={}
                o['type']=k
                o['query_id']=gb_query_id
                o['uid']=as1[0].attrs['href'].encode('utf-8')
                o['pay_type']=tds[2].text.encode('utf-8')
                o['pay_range']=tds[3].text.encode('utf-8')
                o['pay_price']=tds[4].text.encode('utf-8').replace(' CNY','')
                ins_db.wbtc_insert(o)
        except Exception,e:
            logger.debug(e.message)
            logger.error(traceback.format_exc())
        time.sleep(4)



# 创建两个线程
try:
    for k1 in out_u:
        ins_db = mDBA4.A_SDB()
        print k1
        thread.start_new_thread(caiji, (ins_db, k1, out_u[k1]))
except:
    print "Error: unable to start thread"

while 1:
    pass








