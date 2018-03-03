#-*- coding:utf-8 -*-
#     NAME:      mHTTP.py
#     PURPOSE:   HTTP基础类库
#     AUTHOR:    Lin Leiying
#     CREATE:    2017/05/28 23:09

import urllib2
import cookielib
import logging,os,sys,datetime,time
import httplib,ssl,requests
import json,subprocess
import mUtil,mEnv
from PIL import Image



# logging.basicConfig(filename = os.path.join(os.getcwd()+'/logs/',sys.argv[1]+'.log'),
#                     level = logging.DEBUG,
#                     format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s <%(funcName)s> %(message)s',
#                     datefmt='%m%d %H:%M:%S',
#                     )

urllib2.socket.setdefaulttimeout(10)


sess = requests.session()
sess.keep_alive = True


def spyHTTP3(p_url,p_machinetype='macpc',p_referer=None,p_proxy=None,p_mehtod='get',p_data=None,p_header=None):
    FateIp=mUtil.genFateIP()
    print p_url
    logging.debug('Moni:'+FateIp+'/Now Spying/'+p_url)
    '''
    mypayload = {
        'openid':openid,
        'ext':ext,
        'cb': 'sogou.weixin_gzhcb',
        'page': '1',
        'gzhArtKeyWord': '',
        'tsn':'0',
        't':mTOOL.utcUnixFormat(-4),
        '_':mTOOL.utcUnixFormat(-5)
    }
    print query
    mypayload = {
        'type':1,
        'query':query,
        'ie':'utf8'
    }
    '''

    myheaders = {
        'User-Agent':mEnv.env_ua[p_machinetype],
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip',
        'Accept-Language':'zh-CN',
        'remoteAddress':mUtil.genFateIP(),
        'X-Forwarded-For':mUtil.genFateIP(),
        'X-Real-IP':mUtil.genFateIP(),
        'Referer':p_referer,
        'Cookie':mUtil.getMyCookie()
    }

    if p_header is not None:
        for k in p_header:
            myheaders[k]=p_header[k]


    try:
        if p_mehtod=='get':
            r = sess.get(p_url,headers=myheaders,timeout=5)
            logging.debug(r.url)
        if p_mehtod=='post':
            r = sess.post(p_url, headers=myheaders, timeout=5,data=p_data)
            logging.debug(r.url)
        if p_mehtod=='head':
            r = sess.head(p_url, headers=myheaders, timeout=5)
            logging.debug(r.url)
    except requests.exceptions.ConnectionError,fe:
        logging.error('HTTPERROR/'+str(fe.message))
        return 503
    except requests.exceptions.ReadTimeout,fe:
        logging.error('HTTPERROR/'+str(fe.message))
        return 503
    try:
        logging.debug('HTTP-STATUS/'+str(r.status_code))
        if r.status_code==200 and (p_mehtod=='get' or p_mehtod=='post'):
            content=r.content
            logging.debug('Res Length/'+str(len(content)))
            return content
        elif r.status_code==200 and p_mehtod=='head':
            logging.debug('Res Head Ok')
            return r.headers
        else:
            return r.status_code
    except requests.exceptions, e:
        logging.debug('HTTP/'+str(e.code))
        return e.code
    except requests.exceptions.ConnectionError,xe:
        logging.debug('HTTPERROR/'+str(xe.message))
        return 503
    except ssl.SSLError,r:
        logging.error('SSL/'+r.message)
        return 500




def spyHTTP3KuTrace302(p_url,file_type):
    rtn_fname=''
    if len(p_url)>0:
        FateIp=mUtil.genFateIP()
        logging.debug(u'模拟IP:'+FateIp+'/Now Spying/'+p_url)
        myheaders = {
            'User-Agent':mEnv.env_ua['h5'],
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip',
            'Accept-Language':'zh-CN',
            'X-Forwarded-For':FateIp,
            'X-Real-IP':FateIp,
            'Refer':'http://aa.japanfans.com/',
            'Cookie':mUtil.getMyCookie()
        }
        logging.debug(u'开始下载'+p_url.split('/')[2]+u'文件')
        try:
            r = requests.get(p_url,headers=myheaders,timeout=60)
        except Exception,e:
            logging.debug(str(e.message))
            return rtn_fname
        # logging.debug(r.url)
        if r.status_code==200:
            rtn_fname=dest_fileName=r.url.split('?')[0].split('/')[-1]
            logging.debug(u'下载'+dest_fileName+u'成功,大小'+str(len(r.content))+u',开始写文件')
            fdir=mEnv.env_filepath[os.getenv('PYVV')]+file_type+'/'
            f=open(fdir+dest_fileName,'wb')
            f.write(r.content)
            logging.debug(u'写文件成功')
            if file_type=='img':
                try:
                    fImage=Image.open(fdir+dest_fileName)
                    rtn_fname=rtn_fname+'|'+str(fImage.size[0])+'x'+str(fImage.size[1])
                except Exception,e:
                    logging.error(e.message)
                # fImage.destroy()
                # print fImage.size
            f.close()


    return rtn_fname







def spyHTTP6CDNPIC(p_url,xrefer,xqs=None):
    FateIp=mUtil.genFateIP()
    logging.debug('Moni:'+FateIp+'/Now Spying/'+p_url)
    '''
    mypayload = {
        'openid':openid,
        'ext':ext,
        'cb': 'sogou.weixin_gzhcb',
        'page': '1',
        'gzhArtKeyWord': '',
        'tsn':'0',
        't':mTOOL.utcUnixFormat(-4),
        '_':mTOOL.utcUnixFormat(-5)
    }
    print query
    mypayload = {
        'type':1,
        'query':query,
        'ie':'utf8'
    }
    '''

    myheaders = {
        'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip',
        'Accept-Language':'zh-CN',
        'X-Forwarded-For':FateIp,
        'X-Real-IP':FateIp,
        'Refer':xrefer
    }
    try:
        r = requests.get(p_url,headers=myheaders,params=xqs)
    except requests.exceptions.ContentDecodingError,xee:
        logging.debug('HTTPERROR/'+str(xee.message))
        return 400
    logging.debug(r.url)
    #print r.url
    try:
        logging.debug('HTTP-STATUS/'+str(r.status_code))
        if r.status_code==200:
            content=r.content
            logging.debug('Res Length/'+str(len(content)))
            rtnObj={}
            rtnObj['length']=len(content)
            rtnObj['content']=content
            return rtnObj
        else:
            return r.status_code
    except requests.exceptions, e:
        logging.debug('HTTP/'+str(e.code))
        return e.code
    except requests.exceptions.ConnectionError,xe:
        logging.debug('HTTPERROR/'+str(xe.message))
        return 503
    except ssl.SSLError,r:
        logging.error('SSL/'+r.message)
        return 500

