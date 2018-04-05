# -*- coding:utf-8 -*-
'''
币王-Twttier监控
'''

from __future__ import division
import sys
sys.path.append('../')
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

import upyun
from upyun import FileStore
from upyun import print_reporter


bucket_name='shortimgae'
up = upyun.UpYun(bucket_name, 'adminrw', '4444dddd@', timeout=60, endpoint=upyun.ED_AUTO)


def uploadFromLocal(fname,fobj):
    up.put(fname,fobj,need_resume=True,store=FileStore(),reporter=print_reporter)

def downFromSource(url,write_to_fname,write_to_dir):
    img_obj = mHTTP.spyHTTP6CDNPIC(url)
    with open(os.getcwd() + '/'+write_to_dir+'/' + write_to_fname, 'wb') as f:
        f.write(img_obj['content'])
        logger.debug('Image Write Done')
        #继续上传Upyun
        uploadFromLocal(write_to_fname,img_obj['content'])
        logger.debug('Image Upload Done')


for i in range(len(rtn)):
    try:
        public_tweets = api.user_timeline(u8(rtn[i]['name']),tweet_mode='extended',count=10)
        for tweet in public_tweets:
            # print tweet
            # time.sleep(1111)
            o={}
            #推文
            o['name']=u8(rtn[i]['name'])
            o['mtype']='tw'
            o['author']=u8(rtn[i]['name'])
            o['mp_sn']=str(tweet.id)
            o['art_title']=''
            o['art_text']=u8(tweet.full_text)
            o['mp_url']='https://mobile.twitter.com/cnnbrk/status/'+str(o['mp_sn'])
            o['create_at']=tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')  #GMT时间
            o['city_ref']=''
            o['out_type']=''
            o['out_media']=''

            ext_rcd=insdb.sQueryCataArt(o)
            if len(ext_rcd)==1:
                logger.debug('记录已存在，skip')
                continue


            #Profile
            if i<=1:
                o['b']='a'
                o['ava'] = u8(tweet.user.profile_image_url_https).replace('normal','bigger')
                o['screen_name'] = u8(tweet.user.screen_name)
                fname_img_ava=o['ava'].split('/')[-1]
                #下载头像图片
                downFromSource(o['ava'],fname_img_ava,'ava')
                o['ava'] = fname_img_ava

                insdb.sMediaUpdateUserInfo(o)

            # 多媒体图像
            logger.debug(tweet.full_text)
            if hasattr(tweet, 'extended_entities'):
                # print json.dumps(tweet.extended_entities, indent=2)
                media_sets=tweet.extended_entities['media']
                for j in range(len(media_sets)):
                    #break 代表只取第一张
                    if media_sets[j]['type']==u'photo':
                        o['out_type']='img'
                        o['out_media']=u8(media_sets[j]['media_url'])
                        fname_img_sucai=o['out_media'].split('/')[-1]
                        downFromSource(o['out_media'], fname_img_sucai, 'sucai')
                        o['out_media']=fname_img_sucai
                        break
                    if media_sets[j]['type']==u'video':
                        o['out_type'] = 'video'
                        video_info=u8(media_sets[j]['video_info']['variants'][0]['url'])
                        o['out_media']=video_info
                        fname_video_sucai = o['out_media'].split('/')[-1]
                        downFromSource(o['out_media'], fname_video_sucai, 'sucai')
                        o['out_media']=fname_video_sucai
                        break

            # print json.dumps(o,indent=2)
            insdb.sInsertCataArt(o)
        logger.debug('等下一条Twitter主')
    except Exception, e:
        logger.debug('[OHS]' + traceback.format_exc())
        time.sleep(1)

logger.debug('结束')