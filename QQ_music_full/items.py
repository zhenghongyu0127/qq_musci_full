# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class QqMusicFullItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    singer_name = scrapy.Field()
    singer_country = scrapy.Field()
    singer_id = scrapy.Field()
    singer_mid = scrapy.Field()
    singer_music_total = scrapy.Field()
    music_info = scrapy.Field()
    music_track_info = scrapy.Field()
    song_mid = scrapy.Field()

    pass