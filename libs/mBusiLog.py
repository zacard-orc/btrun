#-*- coding:utf-8 -*-
#     NAME:      mBusiLog.py
#     PURPOSE:   日志统一管理
#     AUTHOR:    Lin Leiying
#     CREATE:    2017/05/26 19:05

import datetime as dt
import logging,os

class MyFormatter(logging.Formatter):
    converter=dt.datetime.fromtimestamp
    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            t = ct.strftime("%Y-%m-%d,%H:%M:%S.%f")
            s = "%s,%03d" % (t, record.msecs)
        return s


date_fmt = '%Y%m%d %H:%M:%S.%f'
log_fmt = '%(asctime)s %(filename)s %(lineno)d %(threadName)s %(process)d <%(funcName)s> %(message)s'


def myLog(logfilename,level=logging.DEBUG,testfh=True):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    #log self ins
    xfmt=MyFormatter(fmt=log_fmt,datefmt='%m-%d,%H:%M:%S.%f')

    #console log
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(xfmt)

    # if os.path.exists(os.getcwd()+'/logs/')== False:
    #     os.makedirs(os.getcwd()+'/logs/')

    #file log
    # fh = logging.FileHandler(os.path.join(os.getcwd()+'/../logs/',logfilename), mode='a')
    fh = logging.FileHandler(os.path.join(os.getcwd()+'/',logfilename), mode='a')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(xfmt)

    #addHanle ,可以根据环境切换Console
    if os.getenv('PYVV')=='test':
        # a=1
        logger.addHandler(console)
        logger.addHandler(fh)
        # if testfh==True:
    else:
        logger.addHandler(console)
        logger.addHandler(fh)
    return logger