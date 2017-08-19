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


    def sAdStatsGetPubId(self, o):
        add_sql=''
        if o['acct'] == 'tu':
            add_sql=''
        else:
            add_sql='and acct=\'' + o['pub_acct'] +'\''
        self.sql = 'select acct,pub_name,pub_id from dpp_ad_task where is_block=0 '+add_sql
        logging.debug('查询ACCT下的PUB-ID任务数量')
        return self.OpsSql()

    def sAdClearByPubId(self,o):
        self.sql = 'delete from dpp_ad_main where pub_id=\'' + o['pub_id'] +'\''
        logging.debug('清空原先的任务')
        self.DMLSql()

    def sAdQueryByAcctAndPubId(self, o):
        self.sql = 'select * from dpp_ad_main where pub_id=\''+o['pub_id']+'\' and adp_acct=\''+o['acct']+'\''
        logging.debug('读取该PUB-ID下的广告配置')
        return self.OpsSql()

    def sAdInsertNewAdConfig(self,o):
        self.sql = 'insert into dpp_ad_main(adp_acct,pub_id,pub_sucai,pub_link,pub_obj,pub_sucai_type) values (' \
                   '\'' + o['acct'] +'\',' \
                    '\'' + o['pub_id'] + '\',' \
                    '\'' + o['pub_sucai'] + '\',' \
                    '\'' + o['pub_link'] + '\',' \
                    '\'' + o['pub_obj'] + '\',' \
                    '\'' + o['pub_sucai_type'] + '\'' \
                    ')'
        logging.debug('插入新的广告投放具体配置ByPubId')
        self.DMLSql()


    def slogin_queryByAcct(self,o):
        self.sql='select * from dpp_ad_adpinfo where ' \
                 'adp_acct=\'' + o +'\''
        logging.debug('根据acct查询账户记录')
        return self.OpsSql()

    def sLoadArtTypeList(self):
        self.sql = 'select * from dpp_mp_arttype'
        logging.debug('读取分类枚举值')
        return self.OpsSql()

    def sLoadAdTask(self,o):
        #
        add_sql1=''
        add_sql2 = ' (acct like \'%' + o['setext'] + '%\' ' \
                        ' or pub_name like \'%' + o['setext'] + '%\' ' \
                        ' or pub_id like \'%' + o[
                        'setext'] + '%\') '
        if o['acct']=='tu':
            add_sql1 = ' where '+add_sql2
        else:
            add_sql1 = ' where acct=\'' + o['acct'] + '\' and '+add_sql2

        self.sql = 'select acct,pub_name,pub_id,is_block,' \
                   'date_format(createdAt,\'%m-%d %H:%i\') as createdAt' \
                   ' from dpp_ad_task  '+add_sql1+' order by pub_id desc '
        logging.debug('读取acct下的广告任务')
        return self.OpsSql()

    def sNewAdTask(self,o):
        self.sql = 'insert into dpp_ad_task(acct,pub_name,pub_id,createdAt) values (' \
                   '\'' + o['acct'] +'\',' \
                    '\'' + o['pub_name'] + '\',' \
                    '\'' + o['pub_id'] + '\',' \
                   'now()' \
                    ' )'
        logging.debug('新建广告任务')
        self.DMLSql()


    def sLoadMpInfoBySearch(self,o):
        add_sql=''
        if len(o['setext'])>0:
            add_sql=' and (a.art_mp_name like \'%'+o['setext']+'%\' ' \
                   ' or a.art_title like \'%'+o['setext']+'%\' ' \
                   ' or a.art_type like  \'%'+o['setext']+'%\' ' \
                    'or a.mp_mid like    \'%'+o['setext']+'%\') '

        self.sql = 'select a.mp_mid,a.art_title,a.art_mp_name,a.art_type,a.art_new_url,' \
                   'date_format(a.updateAt,\'%m-%d %H:%i\') as updateAt, ' \
                   ' b.num_pv,b.num_like '\
                   ' from dpp_mp_main a, '\
                   ' dpp_mp_artpv b where a.mp_mid=b.mp_mid  ' \
                   ''+add_sql+' ' \
                   ' order by a.mp_mid  desc limit '+str(o['page'])+',10'
        logging.debug('搜索文章')
        return self.OpsSql()

    def sLoadMpInfoBySearchCount(self,o):
        add_sql=''
        if len(o['setext'])>0:
            add_sql=' and (a.art_mp_name like \'%'+o['setext']+'%\' ' \
                   ' or a.art_title like \'%'+o['setext']+'%\' ' \
                   ' or a.art_type like  \'%'+o['setext']+'%\' ' \
                    'or a.mp_mid like    \'%'+o['setext']+'%\') '

        self.sql = 'select count(*) as cc '\
                   ' from dpp_mp_main a, '\
                   ' dpp_mp_artpv b where a.mp_mid=b.mp_mid  ' \
                   ''+add_sql+' '
        logging.debug('搜索文章获取总数')
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