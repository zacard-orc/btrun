# -*- coding:utf-8 -*-
# btctrade


import os, json, thread, random, time, traceback, re, urllib,requests,datetime
from libs import mHTTP, mBusiLog, mUtil, mEnv, mDBA3


sdb=mDBA3.A_SDB()

xtime=datetime.datetime.now()+datetime.timedelta(minutes=-5*30)
print xtime.strftime('%Y-%m-%d %H:%M:%S')




