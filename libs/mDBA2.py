# -*- coding:utf-8 -*-
#     NAME:      mDBA2.py
#     PURPOSE:   数据库连接池MySQL
#     AUTHOR:    Lin Leiying
#     CREATE:    2017/05/29 09:00

import MySQLdb
import random
import time
import logging,os,sys,json,time,datetime
from DBUtils.PooledDB import PooledDB
import mEnv



runEv=os.getenv('PYVV')
db_host=mEnv.env_dbinfo[runEv]['db_host']
db_user=mEnv.env_dbinfo[runEv]['db_user']
db_passwd=mEnv.env_dbinfo[runEv]['db_passwd']
db_name=mEnv.env_dbinfo[runEv]['db_name']
db_port=mEnv.env_dbinfo[runEv]['db_port']
db_charset=mEnv.env_dbinfo[runEv]['db_charset']
db_conn_num=mEnv.env_dbinfo[runEv]['db_conn_num']
pool = PooledDB(MySQLdb,
                maxconnections=32,mincached=db_conn_num,maxcached=2,maxshared=32,
                host=db_host,
                user=db_user,
                passwd=db_passwd,
                db=db_name,
                port=db_port,
                charset=db_charset
                )
print 'conn DB2 ok'


class A_SDB:
    def __init__(self):
        self.sql=''

    # Data Fix
    def sDataFixHisMaxMin(self):
        #and exn=\'HB\'
        self.sql='replace into wg_hislimit ' \
            'select exn,kp,max(his_high) as d7_high,min(his_low) as d7_low from wb_kline where ' \
            'kutc >= date_add(now(),interval -7 day)   ' \
            'group by exn,kp '
        return self.DMLSql()

    # Radar Load KLineHis
    def sLoadKLineHis(self,o):
        self.sql='select * from wb_kline where  kutc > date_add(now(),interval -5 minute) ' \
                 'and exn=\''+o['exn']+'\' ' \
                 'order by kp,kutc '
        return self.OpsSql()

    # Radar Append PushMsg
    def sPushMsg(self,o):
        self.sql='insert into wb_pushmsg(msg_type,kp,exn,kutc,close,msg_value,msg_body,createAt) values (' \
            '\''+o['msg_type']+'\',' \
            '\''+o['kp']+'\', ' \
            '\''+o['exn']+'\',' \
            '\''+o['kutc']+'\', ' \
            +str(o['close'])+',' \
            '\''+o['msg_value']+'\',' \
            '\''+o['msg_body']+'\',' \
            'now())'
        return self.OpsSql()

    # Radar Append PushMsg
    def sPushMsgAnm(self,o):
        self.sql='insert into wb_gorush(msg_type,kp,exn,kutc,close,msg_value,msg_body,createAt) values (' \
            '\''+o['msg_type']+'\',' \
            '\''+o['kp']+'\', ' \
            '\''+o['exn']+'\',' \
            '\''+o['kutc']+'\', ' \
            +str(o['close'])+',' \
            '\''+o['msg_value']+'\',' \
            '\''+o['msg_body']+'\',' \
            'now())'
        return self.OpsSql()


    # Load
    def sLoadKLine(self,o):
        self.sql='select * from wb_kline where kp=\''+o['kp']+'\'' \
                 ' and kutc > date_add(now(),interval -60 minute)   ' \
                 ' and tp='+o['tp']+' order by kutc desc'
        return self.OpsSql()

    def sLoadKLineForPolicyBase(self,o):
        self.sql='select * from wb_kline where kp=\''+o['kp']+'\'' \
                 ' and kutc > date_add(now(),interval -10 minute)   ' \
                 '  order by kutc desc'
        return self.OpsSql()

    # OpsTrade
    def sBtcInsertOps(self,o):
        self.sql='insert into wb_ops(exn,kp,ddtime,price,vol,direction,profit,rea,pol_name,para) values(' \
                    '\''+o['exn']+'\',' \
                    '\''+o['kp']+'\',' \
                    '\''+o['ddtime']+'\',' \
                    '' + str(o['price']) + ',' \
                    '' + str(o['vol']) + ',' \
                    '\'' + str(o['direction'])+ '\', ' \
                    '' + str(o['profit']) + ',' \
                    '\''+o['rea']+'\',' \
                    '\''+o['pol_name']+'\',' \
                    '\''+o['para']+'\'' \
                    ')'
        self.DMLSql(logflag=False)

    def sBtcLoadLastOps(self,o):
        self.sql='select * from wb_ops where exn=' \
                    '\''+o['exn']+'\' and kp=' \
                    '\''+o['kp']+'\' and ddtime > date_add(now(),interval -24 hour) order by ddtime desc limit 1'
        return self.OpsSql()


    # Insert Or Update
    def sBtcMarkInsert(self,o):
        self.sql = 'replace into wb_new_his values (' \
                    '\''+o['exn']+'\',' \
                    '\''+o['kp']+'\',' \
                    '\''+o['kutc']+'\',' \
                    '' + str(o['price']) + ',' \
                    '' + str(o['b1_p']) + ',' \
                    '' + str(o['b1_a']) + ',' \
                    '' + str(o['s1_p']) + ',' \
                    '' + str(o['s1_a']) + '' \
                    ')'
        logging.debug('插入btc实时行情')
        self.DMLSql()

    def sBtcMarkAccInsert(self,o):
        self.sql = 'replace into wb_kline_acc values (' \
                    '\''+o['exn']+'\',' \
                    '\''+o['kp']+'\',' \
                    '\''+o['kutc']+'\',' \
                    '' + str(o['buy_a']) + ',' \
                    '' + str(o['sell_a']) + ',' \
                    '' + str(o['sw']) + ',' \
                    '' + str(o['buy_big_a']) + ',' \
                    '' + str(o['sell_big_a']) + '' \
                    ')'
        logging.debug('插入btc明细单量、换手、大单量统计')
        self.DMLSql()

    def sBtcMarkKline(self,o):
        self.sql = 'replace into wb_kline ' \
                   ' values (' \
                    '\''+o['exn']+'\',' \
                    '\''+o['kp']+'\',' \
                    '\''+o['kutc']+'\','\
                    +str(o['close'])+','\
                    +str(o['p_ma5']) + ','\
                    + str(o['p_ma30']) + ',' \
                    + str(o['p_ma60']) + ',' \
                    + str(o['angle_v_ma5']) + ','\
                     + str(o['angle_v_ma30']) + ',' \
                     + str(o['angle_v_ma60']) + ',' \
                     + str(o['his_high']) + ',' \
                     + str(o['his_low']) + ',' \
                     + str(o['buy_q']) + ',' \
                     + str(o['sell_q']) + ',' \
                     'now())'
                     # + str(o['b1_p']) + ',' \
                     # + str(o['b1_a']) + ',' \
                     # + str(o['s1_p']) + ',' \
                     # + str(o['s1_a']) + ',now())'
        logging.debug('插入 '+str(o['kp'])+'行情')
        self.DMLSql(logflag=True)

    def sUsdtMarketInsert(self,o):
        self.sql = 'replace into wb_usdt ' \
                   ' values (' \
                    '\''+o['exn']+'\',' \
                    '\''+o['kutc']+'\','\
                    +str(o['sort_id'])+','\
                    '\''+o['direction']+'\','\
                    + str(o['price']) + ',' \
                    + str(o['r_min']) + ',' \
                    + str(o['r_max']) + ',now())'
        logging.debug('插入 USDT行情')
        self.DMLSql(logflag=True)

    def sBtcMarkKlineMAUpdate(self,o):
        self.sql = 'update wb_kline set ' \
                    'p_ma5=' + str(o['p_ma5']) + ',' \
                    'p_ma10=' + str(o['p_ma10']) + ',' \
                    'p_ma20=' + str(o['p_ma20']) + ',' \
                    'p_ma30=' + str(o['p_ma30']) + ',' \
                    'v_ma5=' + str(o['v_ma5']) + ',' \
                    'v_ma10=' + str(o['v_ma10']) + ' ' \
                    ' where exn=' \
                    '\''+o['exn']+'\' and tp=' \
                    '\''+o['tp']+'\' and kp=' \
                    '\''+o['kp']+'\' and kutc=' \
                    '\''+o['kutc']+'\''
        logging.debug('更新虚拟币 k'+str(o['tp'])+'的MA')
        self.DMLSql(logflag=True)

    def sBtcMarkKlineMACDUpdate(self,o):
        self.sql = 'update wb_kline set ' \
                    'dif=' + str(o['dif']) + ', ' \
                    'dea=' + str(o['dea']) + ', ' \
                    'macd=' + str(o['macd']) + ' ' \
                    ' where exn=' \
                    '\''+o['exn']+'\' and tp=' \
                    '\''+o['tp']+'\' and kp=' \
                    '\''+o['kp']+'\' and kutc=' \
                    '\''+o['kutc']+'\''
        logging.debug('更新虚拟币 k'+str(o['tp'])+'的MACD')
        self.DMLSql(logflag=True)

    def sBtcDealHis(self,o):
        self.sql = 'replace into btc_market_dealhis(utc,price,amount,tid,dltype,updateAt) values (' \
                   '\'' + o['utc'] +'\',' \
                    '' + str(o['price']) + ',' \
                    '' + str(o['amount']) + ',' \
                    '\'' + o['tid'] + '\',' \
                    '\'' + o['dltype'] + '\',' \
                    '\'' + o['updateAt'] + '\'' \
                    ')'
        logging.debug('插入btc历史交易')
        self.DMLSql(logflag=False)


    def DMLSql(self,logflag=True):
        try:
            if logflag==True:
                logging.debug(self.sql)
            # if(len(self.sql)<100):
            #     logging.debug(self.sql)
            # else:
            #     logging.debug(self.sql[0:99])
            conn = pool.connection()
            logging.debug('执行时链接数:'+str(pool._connections))
            cur=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
            ares=cur.execute(self.sql)
            time.sleep(0.03)
            logging.debug("Mysql DMLOps "+str(ares))
            cur.close()
            conn.commit()
            conn.close()
            logging.debug('释放后的链接数:'+str(pool._connections))
            return ares
        except MySQLdb.Error,e:
            logging.error("Mysql Error %d: %s" % (e.args[0], e.args[1]))
            return None

    def OpsSql(self,logflag=True):
        cds=False
        try:
            if logflag == True:
                logging.debug(self.sql)
                logging.debug(type(self.sql))

            conn = pool.connection()
            logging.debug('执行时链接数:'+str(pool._connections))
            cur=conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
            cur.execute(self.sql)
            cds=cur.fetchall()
            logging.debug("Mysql PureOps "+str(len(cds)))
            cur.close()
            conn.commit()
            conn.close()
            logging.debug('释放后的链接数:'+str(pool._connections))
            return cds
        except MySQLdb.Error,e:
            logging.error("Mysql Error %d: %s" % (e.args[0], e.args[1]))
            return None