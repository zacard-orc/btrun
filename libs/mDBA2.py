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



    def sBtcMarkInsert(self,o):
        self.sql = 'insert into btc_market_live(utc,last,vol,vol_delta,updateAt) values (' \
                   '' + str(o['time']) +',' \
                    '' + str(o['last']) + ',' \
                    '' + str(o['vol']) + ',' \
                    '' + str(o['vol_delta']) + ',' \
                    '\'' + o['updateAt'] + '\'' \
                    ')'
        logging.debug('插入btc实时行情')
        self.DMLSql()

    def sBtcMarkK5(self,o):
        self.sql = 'replace into btc_market_k5(ddtime,open,high,low,close,vol) values (' \
                   '\'' + o['ddtime'] +'\',' \
                    '' + str(o['open']) + ',' \
                    '' + str(o['high']) + ',' \
                    '' + str(o['low']) + ',' \
                    '' + str(o['close']) + ',' \
                    '' + str(o['vol']) + '' \
                     ')'
        logging.debug('插入btc k5行情')
        self.DMLSql(logflag=False)

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