#-*- coding:utf-8 -*-

#     NAME:      mEnv.py
#     PURPOSE:   基础环境的配置
#     AUTHOR:    Lin Leiying
#     CREATE:    2017/05/27 08:55
import os

env_ua={
   'h5':'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
   # 'macpc':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    'macpc':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/5313.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/5313.36'
}

env_redis={
    'dev':{
        'host':'127.0.0.1',
        'pwd':'d0SK8CJr6Fg0UeZnOs50Dd8QWmyHj5A',
        'port':6380,
        'db':1,
    },
    'test':{
        'host':'127.0.0.1',
        'pwd':'d0SK8CJr6Fg0UeZnOs50Dd8QWmyHj5A',
        'port':6380,
        'db':1,

    },
    'work':{
        'host':'127.0.0.1',
        'pwd':'d0SK8CJr6Fg0UeZnOs50Dd8QWmyHj5A',
        'port':6380,
        'db':1,
    },
    'work_out':{
        'host':'127.0.0.1',
        'pwd':'d0SK8CJr6Fg0UeZnOs50Dd8QWmyHj5A',
        'port':6380,
        'db':1,
    },
    'work_slave':{
        'host':'139.196.121.6',
        'pwd':'d0SK8CJr6Fg0UeZnOs50Dd8QWmyHj5A',
        'port':6380,
        'db':1,
    },
    'work_hy':{
        'host':'139.196.121.6',
        'pwd':'d0SK8CJr6Fg0UeZnOs50Dd8QWmyHj5A',
        'port':6380,
        'db':1,
    },
    'work_wj':{
        'host': 'r-bp1c2b64a1123f94.redis.rds.aliyuncs.com',
        'pwd': 'xlYxbjml6QdGBkzMlf40WMLaWmyHj',
        'port': 6379,
        'db':1
    }
}

env_httpinfo={
    'dev':{
        'wbwash':'http://127.0.0.1:5000'
    },
    'test':{
        'wbwash':'http://127.0.0.1:8010'
    },
    'work':{
        'wbwash':'http://127.0.0.1:8010'
    },
    'work_wj':{
        'wbwash':'http://127.0.0.1:8010'
    }
}

env_dbinfo={
    'dev':{
        # gongsi basic
        # 'db_host':'rm-bp13779hov3wrck4go.mysql.rds.aliyuncs.com',
        # 'db_port': 3306,
        'db_host':'106.14.2.14',
        'db_port': 3306,
        'db_user':'nmw',
        'db_passwd':'8kwIower!q',
        'db_name':'nmw',
        'db_charset':'utf8mb4',
        'db_conn_num':3
    },
    'test':{
        'db_host':'106.14.2.14',
        'db_port': 3306,
        'db_user':'nmw',
        'db_passwd':'8kwIower!q',

        'db_name':'nmw',
        'db_charset':'utf8mb4',
        'db_conn_num':3
    },
     'work':{
        # 'db_host':'106.14.2.14',
        # 'db_port': 3306,
        # 'db_user':'nmw',
        # 'db_passwd':'8kwIower!q',
        # 'db_name':'nmw',
        # 'db_charset':'utf8mb4',
        # 'db_conn_num':3
        # 'db_host':'rm-uf6h56xc3823320z4yo.mysql.rds.aliyuncs.com',
        # 'db_port': 3306,
        # 'db_user':'loan_app',
        # 'db_passwd':'h4Qf1JW4L9ttruKDZzBxcHlYNR3ZHW2',
        # 'db_name':'loan',
        # 'db_charset':'utf8mb4',
        # 'db_conn_num':3,
        'db_host':'rm-uf6h56xc3823320z4yo.mysql.rds.aliyuncs.com',
        'db_port': 3306,
        'db_user':'ft_app',
        'db_passwd':'ENGU0t2H1uxTsBeokLIr3U',
        'db_name':'ft',
        'db_charset':'utf8mb4',
        'db_conn_num':3
    },
     'work_out':{
        'db_host':'106.14.2.14',
        'db_port': 3306,
        'db_user':'nmw',
        'db_passwd':'8kwIower!q',
        'db_name':'nmw',
        'db_charset':'utf8mb4',
        'db_conn_num':3
    },
     'work_hy':{
        'db_host':'106.14.2.14',
        'db_port': 3306,
        'db_user':'nmw',
        'db_passwd':'8kwIower!q',
        'db_name':'nmw',
        'db_charset':'utf8mb4',
        'db_conn_num':3
    }
}

env_path={
    'test':{
        'image':os.getcwd(),
        'video':os.getcwd(),
        'domain':'http://127.0.0.1:3000',
        'uploadpath':'/tmp/img/acc/upload'
    },
    'work':{
        'image':'/home/mp_data',
        'video':'/ndata/mp_data/v',
        'domain':'http://mp.131su.com',
        'uploadpath':'/home/mp_data/img/acc/upload'
    },
    'work_wj':{
        'image':'/ndata/mp_data',
        'video':'/ndata/mp_data/v',
        'domain':'http://mp.weixinqqjs.com',
        'uploadpath':'/ndata/mp_data/img/acc/upload'
    }
}

env_server_ip={
    'test':{
        'ip':'127.0.0.1'
    },
    'work':{
        'ip':'115.238.54.181'
    },
    'work_wj':{
        'ip':'106.14.2.14'
    },
    'work_out':{
        'ip':'106.14.2.14'
    }
}