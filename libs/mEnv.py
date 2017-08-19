#-*- coding:utf-8 -*-

#     NAME:      mEnv.py
#     PURPOSE:   基础环境的配置
#     AUTHOR:    Lin Leiying
#     CREATE:    2017/05/27 08:55
import os

env_ua={
   'h5':'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
   'macpc':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
}

env_redis={
    'test':{
        'host':'127.0.0.1',
        'pwd':'d0SK8CJr6Fg0UeZnOs50Dd8QWmyHj5A',
        'port':6380
    },
    'work':{
        'host': '127.0.0.1',
        'pwd': 'd0SK8CJr6Fg0UeZnOs50Dd8QWmyHj5A',
        'port': 6380
    }
}

env_dbinfo={
    'dev':{
        'db_host':'127.0.0.1',
        'db_user':'stock',
        'db_passwd':'123',
        'db_name':'stock',
        'db_port':3306,
        'db_charset':'utf8',
        'db_conn_num':3
    },
    'test':{
        'db_host': '127.0.0.1',
        'db_user': 'stock',
        'db_passwd': '123',
        'db_name': 'stock',
        'db_port': 3306,
        'db_charset': 'utf8',
        'db_conn_num': 3
    },
    'work':{
        'db_host': '115.238.54.181',
        'db_user': 'stock',
        'db_passwd': '123',
        'db_name': 'stock',
        'db_port': 3306,
        'db_charset': 'utf8',
        'db_conn_num': 3
    },
    'ana':{
            'db_host': '115.238.54.181',
            'db_user': 'stock',
            'db_passwd': '123',
            'db_name': 'stock',
            'db_port': 3306,
            'db_charset': 'utf8',
            'db_conn_num': 3
    }

}

env_path={
    'test':{
        'image':os.getcwd(),
        'domain':'http://127.0.0.1:3000',
        'uploadpath':'/tmp/img/acc/upload'
    },
    'work':{
        'image':'/home/mp_data',
        'domain':'http://mp.131su.com',
        'uploadpath':'/home/mp_data/img/acc/upload'
    }
}

env_server_ip={
    'test':{
        'ip':'127.0.0.1'
    },
    'work':{
        'ip':'115.238.54.181'
    }
}