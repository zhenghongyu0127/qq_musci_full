# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

# import pymongo
# m = pymongo.MongoClient('127.0.0.1')['qq_music']['music_detail']
#
#
# class QqMusicFullPipeline(object):
#     def process_item(self, item, spider):
#         m.insert(dict(item))
#         return item


import pymongo
import redis
import pandas as pd

redis_db = redis.Redis(host='127.0.0.1',port=6379,db=1) # 链接本地redis数据库
redis_data_dict = ''

dic = {} # 创建一个内存字典存储新抓取的歌曲Mid，以防止重复抓取

class MongoRemovePipeline(object):
    def __init__(self):
        self.mongo_con = pymongo.MongoClient('127.0.0.1')['qq_music']

        # redis_db.flushdb() # 清空当前数据库中的所有key，为了后面将mongo数据库中的数据全部保存进去

        if redis_db.hlen(redis_data_dict)==0: #判断redis数据库中的key，如果不存在就读取mongo数据并临时保存在redis中
            mongo_music_url = self.mongo_con['music_detail']
            data = pd.DataFrame(list(mongo_music_url.find())) # 使用pandas读取mongo中歌曲mid表信息
            for i in data['song_mid']:
                print(i)
                redis_db.hset(redis_data_dict,i,0) # 将mongo中歌曲mid表存入redis哈希

    def process_item(self,item,spider):
        # 比较爬取的数据在数据库中是否存在，不存在则插入数据库
        if redis_db.hexists(redis_data_dict,item['song_mid']) and item['song_mid'] in dic.keys(): # 双重判断数据库加内存判断数据是否重复
            return '数据库已经存在该数据，默认不追加'
        else:
            dic[item['song_mid']] = 0
            with open('./track2.txt', 'a+')as x: # 此text文件创建是方便测试用
                x.write(item['song_mid'] + '\n')
            self.do_insert(item)
            return item

    def do_insert(self,item):
        self.mongo_con['music_new_mid'].insert({'song_mid':item['song_mid']}) # 新增歌曲mid加入之前歌曲mid表中,次数据表测试后可以替换成原有歌曲mid的mongo表
        self.mongo_con['music_new_detail'].insert(dict(item)) #本次增量数据插入到新创建的mongo表中


