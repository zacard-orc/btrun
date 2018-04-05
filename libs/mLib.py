#coding=utf-8

import mHTTP
from flask import current_app
import os,random,time,datetime
from PIL import Image
import re


from hashlib import sha1
import hmac

re_wbdatefmt = re.compile("\+\d{4} ")


def wbtsconv(f):
    info = re.sub(re_wbdatefmt, '', f)
    d_fmt=datetime.datetime.strptime(info, "%a %b %d %H:%M:%S %Y")
    return d_fmt.strftime('%Y-%m-%d %H:%M:%S')

def downImg(url,fname_type,webp_extname=None,sn=None):
    fname=url.split('/')[4]
    rtnObj = mHTTP.spyHTTP6CDNPIC(url, xrefer='mp.weixin.qq.com')
    if type(rtnObj) is not int:
        phy_dir = ''
        if fname_type == 'png':
            phy_dir = '/img/'+sn+'/mmbiz_png/'
        if fname_type == 'jpeg' or fname_type=='jpg':
            phy_dir = '/img/'+sn+'/mmbiz_jpg/'
        if fname_type == 'gif':
            phy_dir = '/img/'+sn+'/mmbiz_gif/'
        if fname_type == 'webp':
            fname = webp_extname
            phy_dir = '/img/'+sn+'/mmbiz_webp/'
        if fname_type == 'mp4':
            fname = fname.split('?')[0]
            phy_dir = '/img/'+sn+'/mmbiz_mp4/'

        current_app.logger.debug(phy_dir+'|'+fname_type)
        phy_dir_root = current_app.config.get('IMAGE_PATH')
        print phy_dir_root,phy_dir
        if not os.path.exists(phy_dir_root + phy_dir):
            os.makedirs(phy_dir_root + phy_dir)



        with open(phy_dir_root + phy_dir + fname + '.' + fname_type, 'wb') as f:
            f.write(rtnObj['content'])

        fImage_size_str='640x480'
        fImage=''
        try:
            fImage = Image.open(phy_dir_root + phy_dir + fname + '.' + fname_type)
            fImage_size_str = str(fImage.size[0]) + 'x' + str(fImage.size[1])
        except Exception,e:
            print e.message+','+fname

        if fname_type == 'webp':
            fImage.save(phy_dir_root + phy_dir + fname + '.jpeg', "jpeg")
            fname_type='jpeg'

        gif_1stpic_savepath_web=''
        if fname_type == 'gif':
            current_app.logger.debug(u'对GIF进行拆帧，打开第一帧')
            fImage.seek(0)
            gif_1stpic_savepath_phy = phy_dir_root + '/img/'+sn+'/mmbiz_jpg/' + fname + '_1stpic.jpg'
            gif_1stpic_savepath_web = '/img/'+sn+'/mmbiz_jpg/' + fname + '_1stpic.jpg'
            if not os.path.exists(phy_dir_root + '/img/'+sn+'/mmbiz_jpg/'):
                os.makedirs(phy_dir_root + '/img/'+sn+'/mmbiz_jpg/')
            fImage.convert("RGB").save(gif_1stpic_savepath_phy)
            current_app.logger.debug(u'第一帧转存结束')
        del fImage
        return phy_dir + fname + '.' + fname_type+'|'+fImage_size_str+'|'+gif_1stpic_savepath_web+'|'+str(rtnObj['length'])
    else:
        return None


def random_str(y):
    return ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890',y))

def random_num():
    return str(int(time.time())*1000000+datetime.datetime.now().microsecond)

def u8(o):
    return o.encode('utf-8')


def sha1hamc(plain_txt,shared_key):
    return hmac.new(shared_key,plain_txt, sha1).hexdigest()
