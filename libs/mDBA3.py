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
from mUtil import  u8,printDicEle


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

    def sMediaWeiboList(self,o):
        self.sql='select * from bk_dsms_obj where mtype=\''+o['mtype']+'\' and flag=1;'
        logging.debug('读取'+o['mtype']+'的记录')
        return self.OpsSql()

    def sMediaUpdateUserInfo(self,o):
        self.sql='update bk_dsms_obj ' \
                 'set screen_name=\''+o['screen_name']+'\',ava=\''+o['ava']+'\' where ' \
                 'mtype=\''+o['mtype']+'\' and name=\''+o['name']+'\';'
        self.DMLSql()


    def sExistCataArt(self,o):
        # printDicEle(o)
        self.sql='select count(*) as cc from  bk_cata_art where mtype=' \
                '\''+o['mtype']+'\' and mp_sn=' \
                '\''+o['mp_sn']+'\''
        return self.OpsSql()

    def sInsertCataArt(self,o):
        # printDicEle(o)
        self.sql='insert into bk_cata_art(author,mtype,mp_sn,art_title,art_text,create_at' \
                 ',mp_url,city_ref,out_type,out_media,update_at) values (' \
                '\''+o['author']+'\',' \
                '\''+o['mtype']+'\',' \
                '\''+o['mp_sn']+'\',' \
                '\''+o['art_title']+'\',' \
                '\''+MySQLdb.escape_string(o['art_text'])+'\',' \
                '\''+o['create_at']+'\',' \
                '\''+o['mp_url']+'\',' \
                '\''+o['city_ref']+'\',' \
                '\''+o['out_type']+'\',' \
                '\''+o['out_media']+'\',now())'
        self.DMLSql()

    def sExistCataArtSucai(self,o):
        self.sql='select count(*)  as cc from bk_cata_artsucai where mp_sn=' \
                '\''+o['mp_sn']+'\' and sc_url=' \
                '\''+o['sc_url']+'\''
        return self.OpsSql()

    def sInsertCataArtSucai(self,o):
        self.sql='insert into bk_cata_artsucai(id,mp_sn,sc_url,sc_type) values (' \
                '\''+o['id']+'\',' \
                '\''+o['mp_sn']+'\',' \
                '\''+o['sc_url']+'\',' \
                '\''+o['sc_type']+'\')'
        self.DMLSql()

    def sQueryCataArt(self,o):
        self.sql='select * from bk_cata_art where mp_sn=\''+o['mp_sn']+'\';'
        return self.OpsSql()

    def sLoadKLineBasic(self,o):
        self.sql='select aa.*,bb.* from ( ' \
                 'select a.*,round((a.close-b.d7_low)*100/(b.d7_high-b.d7_low),2)  as pcts ' \
                 'from wb_kline_rq a,wg_hislimit b where a.kp=\''+o['kp']+'\'  and ' \
                 'a.kp=b.kp and b.exn=\'HB\' and a.kutc > date_add(now(),interval -'+str(o['pertime'])+' hour)) aa,' \
                  '(' \
                 'select concat(date_format(kutc,\'%H:\'),floor(date_format(kutc,\'%i\')/5)*5) AS c,' \
                 'round(sum(buy_a)/sum(sell_a),2) as dk_r,' \
                 'round(sum(buy_big_a)/sum(sell_big_a),2) as dk_big_r ' \
                 'from wb_kline_acc where kp=\''+o['kp']+'\' ' \
                'and kutc > date_add(now(),interval -'+str(o['pertime'])+' hour)' \
                 ' and date_format(kutc,\'%i\') >9 ' \
                'group by c ' \
                'union ' \
                'select concat(date_format(kutc,\'%H:0\'),floor(date_format(kutc,\'%i\')/5)*5) AS c,' \
                 'round(sum(buy_a)/sum(sell_a),2) as dk_r,' \
                 'round(sum(buy_big_a)/sum(sell_big_a),2) as  dk_big_r ' \
                'from wb_kline_acc where kp=\''+o['kp']+'\' ' \
                'and kutc > date_add(now(),interval -'+str(o['pertime'])+' hour) ' \
                'and date_format(kutc,\'%i\') <=9 ' \
                'group by c) bb ' \
                'where date_format(aa.kutc,\'%H:%i\')=bb.c order by kutc  '
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