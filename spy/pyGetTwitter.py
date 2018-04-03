# -*- coding:utf-8 -*-
'''
币王-微博监控
'''

from __future__ import division
import os,urllib,time,traceback,json,re,datetime,requests,hashlib,random,tweepy
from libs import mBusiLog,mUtil,mHTTP,mDBA3
from libs.mUtil import u8


logger = mBusiLog.myLog(os.path.basename(__file__).split('.')[0] + '.log')

insdb=mDBA3.A_SDB()
count=0

rtn=insdb.sMediaWeiboList({'mtype':'tw'})
'''
2E80～33FFh：中日韩符号区。收容康熙字典部首、中日韩辅助部首、注音符号、日本假名、韩文音符，中日韩的符号、标点、带圈或带括符文数字、月份，以及日本的假名组合、单位、年号、月份、日期、时间等。
3400～4DFFh：中日韩认同表意文字扩充A区，总计收容6,582个中日韩汉字。
4E00～9FFFh：中日韩认同表意文字区，总计收容20,902个中日韩汉字。
A000～A4FFh：彝族文字区，收容中国南方彝族文字和字根。
AC00～D7FFh：韩文拼音组合字区，收容以韩文音符拼成的文字。
F900～FAFFh：中日韩兼容表意文字区，总计收容302个中日韩汉字。
FB00～FFFDh：文字表现形式区，收容组合拉丁文字、希伯来文、阿拉伯文、中日韩直式标点、小符号、半角符号、全角
'''
regex=u"[\u2E80-\u9FFF]+"

# 填写twitter提供的开发Key和secret
consumer_key = 'QF5KIv0ne8DobbIwqwDhYPATM'
consumer_secret = 'XfrBtJ4JYTFPshi4dG2D5mM7q3Yx8i6rOynqntu8bTG0qkRG5H'
access_token = '2223072025-t0SSFLePAVjlWACB9LAACmdK496J0wwB0SsKrBn'
access_token_secret = 'K2eqwGMJyMjR6haeSRCp69wmF4qDJsXRUOn7eq67wRlLi'

# 提交你的Key和secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
# 获取类似于内容句柄的东西
api = tweepy.API(auth)

#jieba add word
# jieba.load_userdict(os.getcwd()+'/userdict.txt')
# logger.debug(os.getcwd()+'/userdict.txt')


for i in range(len(rtn)):
    try:
        public_tweets = api.user_timeline(u8(rtn[i]['name']))
        for tweet in public_tweets:
            print tweet.created_at
            if hasattr(tweet, 'extended_entities'):
                print json.dumps(tweet.extended_entities, indent=2)

        logger.debug('等下一条Twitter主')
    except Exception, e:
        logger.debug('[OHS]' + traceback.format_exc())
    time.sleep(9)

logger.debug('结束')