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
print 'conn DB3 ok'

class A_SDB:
    def __init__(self):
        self.sql=''

    def slogin_queryByAcct(self,o):
        self.sql='select * from rpmall_userinfo where ' \
                 'acct=\'' + o +'\''
        logging.debug('根据acct查询账户记录')
        return self.OpsSql()



    #文章基础库
    def sD_mpMain_Insert(self,o):
        self.sql='replace into dpp_mp_main values(' \
                 '\'' + o['mp_biz'] +'\',' \
                 '\'' + o['mp_mid'] +'\',' \
                 '\'' + o['mp_sn'] +'\',' \
                 '\'' + o['mp_idx'] +'\',' \
                 '\'' + MySQLdb.escape_string(o['art_title']) + '\',' \
                 '\'' + MySQLdb.escape_string(o['art_mp_name']) + '\',' \
                 '\'' + o['art_pubdate'] + '\',' \
                 '\'' + MySQLdb.escape_string(o['art_author_name']) + '\',' \
                 '\'' + o['art_type'] + '\',' \
                 '\'' + o['art_origin_url'] + '\',' \
                  '\'' + o['art_new_url'] + '\',' \
                  'now())'
        self.DMLSql(logflag=True)

    def sD_mpMainQrcode_Query(self,o):
        self.sql='select qrcode_path from dpp_mp_qrcode where  ' \
                 'mp_biz=\'' + o['mp_biz'] +'\' '
        return self.OpsSql(logflag=True)

    def sD_mpMainQrcode_Replace(self, o):
        self.sql = 'replace into dpp_mp_qrcode values (  ' \
                   '\'' + o['mp_biz'] + '\', ' \
                   '\'' + o['qrcode_path'] + '\', now())'
        self.DMLSql(logflag=True)

    def sD_mpSucai_Clear(self,o):
        self.sql='delete from dpp_mp_artsucai where mp_mid=\'' + o['mp_mid'] + '\';'
        self.DMLSql(logflag=True)

    def sD_mpSucai_Insert(self,o):
        self.sql='insert into dpp_mp_artsucai values(' \
                 '\'' + o['mp_mid'] +'\',' \
                 '\'' + o['sc_url'] +'\',' \
                 '\'' + o['sc_type'] +'\',' \
                 '\'' + o['sc_size'] + '\',' \
                 'now()' \
                 ')'
        self.DMLSql(logflag=True)

    def sD_mpHtml_Insert(self,o):
        self.sql = 'replace into dpp_mp_arthtml values(' \
                   '\'' + o['mp_mid'] + '\',' \
                    '\'' + MySQLdb.escape_string(o['art_html']) + '\',' \
                   'now()' \
                   ')'
        self.DMLSql(logflag=False)

    def sD_mpPv_IfExist(self,o):
        self.sql = 'select count(*) as cc from dpp_mp_artpv where mp_mid=' \
               '\'' + o['mp_mid'] + '\' '
        return self.OpsSql(logflag=False)

    def sD_mpPv_insert(self,o):
        self.sql = 'replace into dpp_mp_artpv values(' \
                   '\'' + o['mp_mid'] + '\',' \
                   '' + str(o['num_pv']) + ',' \
                   '' + str(o['num_like']) + ',' \
                   'now()' \
                   ')'
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