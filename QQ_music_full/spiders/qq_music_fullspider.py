# -*- coding: utf-8 -*-
import scrapy
import json


from QQ_music_full.items import QqMusicFullItem

class QqMusicFullspiderSpider(scrapy.Spider):
    name = "qq_music_fullspider"
    # allowed_domains = ["www"]
    start_urls = []
    for i in range(1,9810):
        # 拼接入口url加入待爬队列
        url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?data={"comm":{"ct":24,"cv":0},"singerList":{"module":"Music.SingerListServer","method":"get_singer_list","param":{"area":-100,"sex":-100,"genre":-100,"index":-100,"sin":'+str((i-1)*80)+',"cur_page":'+str(i)+'}}}'
        start_urls.append(url)
    def parse(self, response): # 首先获取歌手mid，利用歌手mid来拼接成每个歌手对应的歌曲信息列表，通过分析json信息发现全部歌手23705条
        singer_json = json.loads(response.text)
        for sin_json in singer_json['singerList']['data']['singerlist']:
            singer_country = sin_json['country']
            singer_mid = sin_json['singer_mid']
            singer_id = sin_json['singer_id']
            singer_name = sin_json['singer_name']
            # print(singer_name+'\t'+singer_country)
            headers = {
                'referer': 'https://y.qq.com/n/yqq/singer/'+singer_mid+'.html',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
            }
            # 根据歌手的Mid拼接歌手下对应歌曲url
            singer_music_url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&ct=24&singermid={}&order=listen&begin=0&num=1'.format(singer_mid)
            yield scrapy.Request(singer_music_url,self.singer_music_parse1,meta={
                'singer_name':singer_name,
                'singer_country':singer_country,
                'singer_id':singer_id,
                'singer_mid':singer_mid
            },headers=headers)

    # 第一次解析出歌手下对应歌曲数量，拼接url抓取全量
    def singer_music_parse1(self,response):
        singer_music_json = json.loads(response.text)
        singer_name = response.meta['singer_name'] # 歌手名
        singer_country = response.meta['singer_country'] # 歌手归属地
        singer_id = response.meta['singer_id'] # 歌手id
        singer_mid = response.meta['singer_mid'] # 歌手mid
        singer_music_total = singer_music_json['data']['total'] # 歌手单曲量
        headers = {
            'referer': 'https://y.qq.com/n/yqq/singer/' + singer_mid + '.html',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        }
        singer_music_url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&ct=24&singermid={}&order=listen&begin=0&num={}'.format(singer_mid,singer_music_total)
        yield scrapy.Request(singer_music_url, self.singer_music_parse2, meta={
            'singer_name': singer_name,
            'singer_country': singer_country,
            'singer_id': singer_id,
            'singer_mid': singer_mid
        }, headers=headers)

    # 抓取歌手对应全量歌曲
    def singer_music_parse2(self, response):
        singer_music_json = json.loads(response.text)
        singer_name = response.meta['singer_name']  # 歌手名
        singer_country = response.meta['singer_country']  # 歌手归属地
        singer_id = response.meta['singer_id']  # 歌手id
        singer_mid = response.meta['singer_mid']  # 歌手mid
        singer_music_total = singer_music_json['data']['total']  # 歌手单曲量

        # 循环歌手对应歌曲列表取出单个歌曲对应信息
        for singer_music in singer_music_json['data']['list']:
            songmid = singer_music['musicData']['songmid']
            song_id = singer_music['musicData']['songid']
            headers = {
                'referer': 'https://y.qq.com/n/yqq/song/001TXSYu1Gwuwv.html',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
                       }
            music_detail_url = 'https://u.y.qq.com/cgi-bin/musicu.fcg?data={"comm":{"ct":24,"cv":0},"songinfo":{"method":"get_song_detail_yqq","param":{"song_type":0,"song_mid":"'+songmid+'","song_id":'+str(song_id)+'},"module":"music.pf_song_detail_svr"}}'
            yield scrapy.Request(music_detail_url,self.music_detail_parse,meta={
                'singer_name': singer_name,
                'singer_country': singer_country,
                'singer_id': singer_id,
                'singer_mid': singer_mid,
                'singer_music_total':singer_music_total,
                'songmid':songmid
            },headers=headers)

    # 歌曲详情页解析
    def music_detail_parse(self,response):
        music_detail_json = json.loads(response.text)
        singer_name = response.meta['singer_name']  # 歌手名
        singer_country = response.meta['singer_country']  # 歌手归属地
        singer_id = response.meta['singer_id']  # 歌手id
        singer_mid = response.meta['singer_mid']  # 歌手mid
        singer_music_total =  response.meta['singer_music_total'] # 歌手单曲量

        music_info = music_detail_json['songinfo']['data']['info']
        music_track_info = music_detail_json['songinfo']['data']['track_info']
        item = QqMusicFullItem()
        item['singer_name'] = singer_name
        item['singer_country'] = singer_country
        item['singer_id'] = singer_id
        item['singer_mid'] = singer_mid
        item['singer_music_total'] = singer_music_total
        item['music_info'] = music_info
        item['music_track_info'] = music_track_info

        item['song_mid'] = response.meta['songmid']
        yield item


