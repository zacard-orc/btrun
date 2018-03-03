#-*- coding:utf-8 -*-
#     NAME:      mUtil.py
#     PURPOSE:   常用的一些工具函数
#     AUTHOR:    Lin Leiying
#     CREATE:    2017/05/26 21:37

from __future__ import division
import  hashlib,random,re,time,datetime,math,logging

link = re.compile("(</?(a|i|s)? .*['|\"]>)*")

def getMyCookie():
    m2 = hashlib.md5()
    seed=random.uniform(1,100)
    m2.update(str(seed))
    xseed=m2.hexdigest()
    basecookie='_T_WM='+xseed+'; M_WEIBOCN_PARAMS=featurecode%3D20000181%26fid%3D100505'+'%26uicode%3D10000011'
    return basecookie


def genFateIP():
    unitlist=range(1,253)
    unitip = random.sample(unitlist,4)
    unitip[0]=str(unitip[0])
    unitip[1]=str(unitip[1])
    unitip[2]=str(unitip[2])
    unitip[3]=str(unitip[3])
    return '.'.join(unitip)

def washWeiboText(str):
    s1=re.sub(link,'',str)
    s1=s1.replace('</a>','').replace('<br/>','')
    return s1

def printDicEle(o):
    for key in o:
        print key,type(o[key])

def random_str(y):
    return ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890',y))


def UTCtoSTDStamp(a):
    dtstr = '1970-01-01 00:00:00'
    utcstartstamp=datetime.datetime.strptime(dtstr, "%Y-%m-%d %H:%M:%S")
    comafterstamp=utcstartstamp+datetime.timedelta(seconds=int(a),hours=8)
    return comafterstamp.strftime("%Y-%m-%d %H:%M:%S")

def getAngleByKRate(o):
    return round(math.atan(o)*180/math.pi,2)

def TimeStampNowStr():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def random_str_hsf():
    #FBOBZ-VODWU-C7SVF-B2BDI-1K3JE-YBFUS
    a=''
    for i in range(1,36):
        if i%6==0 and i>0:
            a+='-'
        else:
            a+=random.sample('ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890',1)[0]
    return a


def random_num():
    return str(int(time.time())*1000000+datetime.datetime.now().microsecond)

def u8(o):
    return o.encode('utf-8')

def color_distance(o1,o2):
    # return abs(o1[0]-o2[0])+abs(o1[1]-o2[1])+abs(o1[2]-o2[2])
    return math.sqrt((o1[0]-o2[0])**2+(o1[1]-o2[1])**2+(o1[2]-o2[2])**2)

#TODO 构造基础坐标系的转换
# print random_str_hsf()

class A_LLC:
    def __init__(self,lat,lon):
        logging.debug('[I]'+str(lon)+','+str(lat))
        self.lat=lat
        self.lon=lon
        self.gcj_lat=0
        self.gcj_lon=0
        self.bd_lat=0
        self.bd_lon=0
        self.PI=3.14159265358979324
        self.x_pi=3.14159265358979324 * 3000.0 / 180.0

    def __transformLat(self,x,y):
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
        ret += (20.0 * math.sin(6.0 * x * self.PI) + 20.0 * math.sin(2.0 * x * self.PI)) * 2.0 / 3.0
        ret += (20.0 * math.sin(y * self.PI) + 40.0 * math.sin(y / 3.0 * self.PI)) * 2.0 / 3.0
        ret += (160.0 * math.sin(y / 12.0 * self.PI) + 320 * math.sin(y * self.PI / 30.0)) * 2.0 / 3.0
        return ret

    def __transformLon(self,x,y):
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
        ret += (20.0 * math.sin(6.0 * x * self.PI) + 20.0 * math.sin(2.0 * x * self.PI)) * 2.0 / 3.0
        ret += (20.0 * math.sin(x * self.PI) + 40.0 * math.sin(x / 3.0 * self.PI)) * 2.0 / 3.0
        ret += (150.0 * math.sin(x / 12.0 * self.PI) + 300.0 * math.sin(x / 30.0 * self.PI)) * 2.0 / 3.0
        return ret

    def outOfChina(self,lat, lon):
        if (lon < 72.004 or lon > 137.8347):
            return True
        if (lat < 0.8293 or lat > 55.8271):
            return True
        return False

    def delta(self,lat,lon):
        a = 6378245.0 # a: 卫星椭球坐标投影到平面地图坐标系的投影因子。
        ee = 0.00669342162296594323; # ee: 椭球的偏心率。
        dLat = self.__transformLat(lon - 105.0, lat - 35.0);
        dLon = self.__transformLon(lon - 105.0, lat - 35.0);
        radLat = lat / 180.0 * self.PI
        magic = math.sin(radLat)
        magic = 1 - ee * magic * magic
        sqrtMagic = math.sqrt(magic)
        dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * self.PI)
        dLon = (dLon * 180.0) / (a / sqrtMagic * math.cos(radLat) * self.PI)
        return {'lat': dLat, 'lon': dLon}



    def wgs84_to_gcj02(self):
        if self.outOfChina(self.lat, self.lon):
            return {'lat': self.lat, 'lon': self.lon}

        d = self.delta(self.lat, self.lon)
        self.gcj_lat=self.lat + d['lat']
        self.gcj_lon=self.lon + d['lon']


    def gcj02_to_bd09(self):
        x = self.gcj_lon
        y = self.gcj_lat
        z = math.sqrt(x * x + y * y) + 0.00002 * math.sin(y * self.x_pi)
        theta = math.atan2(y, x) + 0.000003 * math.cos(x * self.x_pi)
        bdLon = z * math.cos(theta) + 0.0065
        bdLat = z * math.sin(theta) + 0.006
        self.bd_lat=bdLat
        self.bd_lon=bdLon
        print '[O]',self.bd_lon,self.bd_lat

    def mercator_inner(self):
        x = self.bd_lon * 20037508.34 / 180
        y = math.log(math.tan((90. + self.bd_lat) * self.PI / 360.)) / (self.PI / 180.)
        y = y * 20037508.34 / 180.
        # print '[O]',x,y
        return {'lat': y, 'lon': x}

    def mercator_outer(self):
        x = self.lon * 20037508.34 / 180
        y = math.log(math.tan((90. + self.lat) * self.PI / 360.)) / (self.PI / 180.)
        y = y * 20037508.34 / 180.
        # print '[O]',x,y
        return {'lat': y, 'lon': x}

# 116.405419,39.918255
# 114.21892734521,29.575429778924
# 墨卡托转wgs http://www.site-digger.com/tools/mct2latlng.html
# inswgs=A_LLC(29.575429778924,114.21892734521)
# inswgs.wgs84_to_gcj02()
# inswgs.gcj02_to_bd09()
# inswgs.mercator_inner()
# inswgs.mercator_outer()

# print str(int(time.time()))+str(random.randint(100,999))
#1516920473268
#1516931416432
#1516931334.26

