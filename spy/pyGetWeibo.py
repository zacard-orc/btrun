# -*- coding:utf-8 -*-
'''
币王-微博监控
'''

from __future__ import division
import sys
sys.path.append('../')

import os,urllib,time,traceback,json,re,datetime,requests,hashlib,random,time
from libs import mBusiLog,mUtil,mHTTP,mDBA3
from libs.mUtil import u8
import urlparse
import jieba
import jieba.posseg as pseg

logger = mBusiLog.myLog(os.path.basename(__file__).split('.')[0] + '.log')

insdb=mDBA3.A_SDB()
count=0

rtn=insdb.sMediaWeiboList({'mtype':'wb'})
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
re_h=re.compile('</?\w+[^>]*>')#HTML标签


#jieba add word
jieba.load_userdict(os.getcwd()+'/userdict.txt')
logger.debug(os.getcwd()+'/userdict.txt')


for i in range(len(rtn)):
    try:
        des_url = rtn[i]['url']
        logger.debug(des_url)
        ulp = urlparse.urlparse(des_url)
        v_qsparams = urlparse.parse_qs(ulp.query, True)
        uid = v_qsparams['uid'][0]
        containerid = v_qsparams['lfid'][0]
        logger.debug(uid + ',' + containerid)

        con_url = 'https://m.weibo.cn/api/container/getIndex?uid=' + uid + '&containerid=' + containerid

        wb_m_rtn = mHTTP.spyHTTP3(con_url)
        if type(wb_m_rtn) is int:
            continue

        wb_m_rtn = json.loads(wb_m_rtn)
        card_rtn = wb_m_rtn['data']['cards']

        logger.debug('共有' + str(len(card_rtn)) + '条微博可更新')

        if len(card_rtn) == 0:
            continue

        for z in range(len(card_rtn)):


            if card_rtn[z].has_key('mblog'):
                mblog=card_rtn[z]['mblog']
                o={}
                o['mtype']='wb'
                o['name']=u8(rtn[i]['name'])
                o['mp_sn']=u8(mblog['mid'])
                o['mp_url']='https://m.weibo.cn/status/'+u8(mblog['mid'])

                o['ava']=u8(mblog['user']['avatar_hd'])
                o['screen_name']=u8(mblog['user']['screen_name'])

                if z<=1:
                    #少调用数据库
                    insdb.sMediaUpdateUserInfo(o)

                tmp_crat=u8(mblog['created_at'])
                o['create_at'] = '2018-'+u8(mblog['created_at'])+' 00:00:00'   #EST时间
                if tmp_crat.find('分钟前')>=0:
                    tnum=tmp_crat.replace('分钟前','')
                    this_day = datetime.datetime.now() + datetime.timedelta(minutes=-int(tnum))
                    o['create_at'] = this_day.strftime('%Y-%m-%d %H:%M:%S')

                if tmp_crat.find('小时前')>=0:
                    tnum=tmp_crat.replace('小时前','')
                    this_day = datetime.datetime.now() + datetime.timedelta(hours=-int(tnum))
                    o['create_at'] = this_day.strftime('%Y-%m-%d %H:%M:%S')

                if tmp_crat.find('天前')>=0:
                    tnum=tmp_crat.replace('天前','')
                    this_day = datetime.datetime.now() + datetime.timedelta(days=-int(tnum))
                    o['create_at'] = this_day.strftime('%Y-%m-%d %H:%M:%S')

                if tmp_crat.find('昨天')>=0:
                    tnum=tmp_crat.replace('昨天 ','')
                    this_day = datetime.datetime.now() + datetime.timedelta(days=-1)
                    o['create_at'] = this_day.strftime('%Y-%m-%d ')+tnum

                o['out_media']=''
                o['out_type']=''

                if mblog.has_key('pics'):
                    o['out_type']='img'
                    o['out_media']=u8(mblog['pics'][0]['large']['url'])
                    # TODO 取出所有的素材
                    for m in range(len(mblog['pics'])):
                        so={}
                        so['mp_sn']=o['mp_sn']
                        so['sc_url']=u8(mblog['pics'][m]['large']['url'])
                        so['sc_type']='img'
                        scrtn=insdb.sExistCataArtSucai(so)
                        if scrtn[0]['cc']==0:
                            insdb.sInsertCataArtSucai(so)

                if mblog.has_key('page_info'):
                    if u8(mblog['page_info']['type'])=='video':
                        o['out_type']='video'
                        #封面+视频
                        o['out_media']=u8(mblog['page_info']['page_pic']['url'])+\
                                       ','+u8(mblog['page_info']['media_info']['stream_url'])
                    if u8(mblog['page_info']['type'])=='article':
                        o['out_type']='article'
                        o['out_media']=u8(mblog['page_info']['page_pic']['url'])+\
                                       ','+u8(mblog['page_info']['page_url'])



                o['author']=u8(rtn[i]['name'])
                o['art_title']=''
                o['art_text']=u8(mblog['text'])
                # print o['art_text']
                text_wash=re_h.sub('', o['art_text'])
                text_wash=text_wash.replace('网页链接','').replace('全文','').replace('...','')

                o['art_text']=text_wash
                if o['art_text'].find('】')>0 and o['art_text'].find('【')>=0:
                    o['art_title']=o['art_text'].split('】')[0].split('【')[1]
                else:
                    o['art_title']=''

                words = pseg.cut(o['art_text'])
                ref_word=set()
                o['city_ref']=''
                for word, flag in words:
                    if flag=='ns':
                        ref_word.add(word)

                o['city_ref']=u8(','.join(list(ref_word)))
                o['mtype']='wb'
                catartn=insdb.sExistCataArt(o)
                if catartn[0]['cc']==0:
                    insdb.sInsertCataArt(o)


        logger.debug('等下一条微博主')
    except Exception, e:
        logger.debug('[OHS]' + traceback.format_exc())
    time.sleep(9)

logger.debug('结束')