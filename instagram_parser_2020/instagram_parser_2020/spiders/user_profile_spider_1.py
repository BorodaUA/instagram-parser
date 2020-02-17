# -*- coding: utf-8 -*-
import glob
import json
import os
import urllib
from datetime import date

import pandas as pd
import scrapy
from inline_requests import inline_requests
from scrapy import signals
from scrapy.http import Request
from scrapy.utils.response import open_in_browser
from scrapy.xlib.pydispatch import dispatcher


class UserProfileSpider1Spider(scrapy.Spider):
    name = 'user_profile_spider_1'

    
    def __init__(self):
        self.result_lst = []
        dispatcher.connect(self.my_spider_closed, signals.spider_closed)

    
    def start_requests(self):
        all_hashtags_paths = glob.glob('results/*/*.csv')
        for path in all_hashtags_paths:
            open_df = pd.read_csv(path, index_col=0)
            for url in open_df['full_user_url'].unique():
                meta_dict = {'ht_name':open_df.loc[0,'hashtag_name']}
                yield Request(url=url, meta=meta_dict, callback=self.parse)
                
        
    def parse(self, response):
        start = response.xpath('/html/body/script[1]').get()
        half_clean = start.replace('<script type="text/javascript">window._sharedData = ','').replace(';</script>', '')
        clean_dict = json.loads(half_clean)

        result_dict = {}
        #result_dict['csrf_token'] = clean_dict["config"]['csrf_token']
        result_dict['hashtag_name'] = response.meta['ht_name']
        result_dict['full_name'] = clean_dict['entry_data']['ProfilePage'][0]['graphql']['user']['full_name']
        result_dict['user_id'] = clean_dict['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        result_dict['bio'] = clean_dict['entry_data']['ProfilePage'][0]['graphql']['user']['biography']
        result_dict['followers_count'] = clean_dict['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count']
        result_dict['user_follows'] = clean_dict['entry_data']['ProfilePage'][0]['graphql']['user']['edge_follow']['count']
        result_dict['publications'] = clean_dict['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['count']
        result_dict['profile_url'] = response.url
        self.result_lst.append(result_dict)
    
    
    def my_spider_closed(self, spider):
        hashtag_df = pd.DataFrame(self.result_lst)
        for ht in hashtag_df['hashtag_name'].unique():
            df_to_save = hashtag_df.loc[hashtag_df['hashtag_name'] == ht]
            results_hashtag_path = f'results/{ht}/profiles/'
            if not os.path.exists(results_hashtag_path):
                os.makedirs(results_hashtag_path)
            df_to_save.reset_index(inplace=True, drop=True)
            df_to_save.to_csv(f'{results_hashtag_path}{ht}_profiles.csv', index=True, header=True)
