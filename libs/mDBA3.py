# -*- coding:utf-8 -*-
#     NAME:      mDBA3.py
#     PURPOSE:   数据库连接池MySQL
#     AUTHOR:    Lin Leiying
#     CREATE:    2017/05/29 09:00

import MySQLdb
import random
import time
import logging,os,sys,json,time,datetime
from DBUtils.PooledDB import PooledDB
import mEnv
from mUtil import  u8


runEv='ana'
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
print 'conn DB3 ok'

class A_SDB:
    def __init__(self):
        self.sql=''

    def sbtc_loadk5(self,o):
        self.sql='select * from btc_market_k5 where ' \
                 'ddtime >= \'' + o['sttime_flag'] +'\' order by ddtime'
        logging.debug('读取K5 30*5分钟内记录')
        return self.OpsSql()





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