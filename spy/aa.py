# -*- coding:utf-8 -*-
'''
'''

from __future__ import division
import sys
sys.path.append('../')
import os,urllib,time,traceback,json,re,datetime,requests,hashlib,random,tweepy
from libs import mBusiLog,mUtil,mHTTP,mDBA3
from libs.mUtil import u8


base_url='https://api.twitter.com/2/timeline/conversation/989179898370539520.json?include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_reply_count=1&tweet_mode=extended&include_entities=true&include_user_entities=true&include_ext_media_color=true&send_error_codes=true&count=20'


ph={
    'authorization':'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
}

rtn=mHTTP.spyHTTP3(base_url,p_header=ph)

print rtn