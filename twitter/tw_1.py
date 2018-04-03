# -*- coding:utf-8 -*-
# Twitter测试

# 导入tweepy
import tweepy,time,json


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

# 打印其他用户主页上的时间轴里的内容
public_tweets = api.user_timeline('BMW')

for tweet in public_tweets:
    # print tweet
    print tweet.created_at
    # print tweet.entities
    if hasattr(tweet, 'extended_entities'):
        # print tweet.extended_entities
        print json.dumps(tweet.extended_entities,indent=2)

    # for d in tweet:
    #     print d,tweet[d]
    # print json.dumps(tweet)
    # time.sleep(1999)
