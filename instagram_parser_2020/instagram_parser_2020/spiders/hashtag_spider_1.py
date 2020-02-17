# -*- coding: utf-8 -*-
import json
import os
import urllib
from datetime import date

import pandas as pd
import scrapy
from scrapy.http import Request
from scrapy.utils.response import open_in_browser
from inline_requests import inline_requests


class HashtagSpider1Spider(scrapy.Spider):
    name = 'hashtag_spider_1'

    
    def __init__(self):
        self.result_lst = []
        self.today_date = date.today()
        
        
    def start_requests(self):
        try:
            with open('hashtags_to_parse.txt', 'r', encoding='utf-8') as f:
                hashtags = f.readlines()
                for h_tag in hashtags:
                    yield Request(url=h_tag+'?__a=1', callback=self.parse)
        except FileNotFoundError:
            print('Please provide hashtags_to_parse.txt in the project folder')
    
    
    def parse(self, response):
        dict_response = json.loads(response.body_as_unicode())
        hashtag_name = dict_response['graphql']['hashtag']['name']
        top_posts = dict_response['graphql']['hashtag']['edge_hashtag_to_top_posts']['edges']
        for user in top_posts:
            result_dict = {}
            short_code = user['node']['shortcode']
            result_dict['hashtag_name'] = dict_response['graphql']['hashtag']['name']
            result_dict['owner_id'] = user['node']['owner']['id']
            result_dict['short_code'] = short_code
            result_dict['likes_count'] = user['node']['edge_liked_by']['count']
            result_dict['comments_count'] = user['node']['edge_media_to_comment']['count']
            result_dict['post_description'] = user['node']['edge_media_to_caption']['edges'][0]['node']['text']
            self.result_lst.append(result_dict)
        
        
        newest_posts = dict_response['graphql']['hashtag']['edge_hashtag_to_media']['edges']
        for user in newest_posts:
            result_dict = {}
            short_code = user['node']['shortcode']
            result_dict['hashtag_name'] = dict_response['graphql']['hashtag']['name']
            result_dict['owner_id'] = user['node']['owner']['id']
            result_dict['short_code'] = short_code
            result_dict['likes_count'] = user['node']['edge_liked_by']['count']
            result_dict['comments_count'] = user['node']['edge_media_to_comment']['count']
            result_dict['post_description'] = user['node']['edge_media_to_caption']['edges'][0]['node']['text']
            self.result_lst.append(result_dict)

        next_page = dict_response['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']
        end_cursor = dict_response['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
        
        after_value = f',"after":"{end_cursor}"' if end_cursor else ''
        hash_tag_name = dict_response['graphql']['hashtag']['name']
        variables_value = f'{{"tag_name":"{hash_tag_name}","first":25{after_value}}}'
        params = {
            'query_hash':'174a5243287c5f3a7de741089750ab3b',
            'variables':variables_value,
        }
        cooler_params = urllib.parse.urlencode(params)
        next_tags_url = f'https://www.instagram.com/graphql/query/?{cooler_params}'
        
        #if next_page == True:
        yield Request(
            url=next_tags_url,
            method='GET',
            callback=self.next_hashtags,
        )
       

    def next_hashtags(self, response):
        dict_response = json.loads(response.body_as_unicode())
       
        next_newest_posts = dict_response['data']['hashtag']['edge_hashtag_to_media']['edges']
        for user in next_newest_posts:
            result_dict = {}
            short_code = user['node']['shortcode']
            result_dict['hashtag_name'] = dict_response['data']['hashtag']['name']
            result_dict['owner_id'] = user['node']['owner']['id']
            result_dict['short_code'] = short_code
            result_dict['likes_count'] = user['node']['edge_liked_by']['count']
            result_dict['comments_count'] = user['node']['edge_media_to_comment']['count']
            try:
                result_dict['post_description'] = user['node']['edge_media_to_caption']['edges'][0]['node']['text']
            except IndexError:
                result_dict['post_description'] = None
            self.result_lst.append(result_dict)

            
        next_page = dict_response['data']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']
        end_cursor = dict_response['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']    
        hashtag_name = dict_response['data']['hashtag']['name']
        
        after_value = f',"after":"{end_cursor}"' if end_cursor else ''
        variables_value = f'{{"tag_name":"{hashtag_name}","first":75{after_value}}}'
        params = {
            'query_hash':'174a5243287c5f3a7de741089750ab3b',
            'variables':variables_value,
        }
        cooler_params = urllib.parse.urlencode(params)
        next_tags_url = f'https://www.instagram.com/graphql/query/?{cooler_params}'

        get_next_tags_request = Request(
            url=next_tags_url,
            method='GET',
            callback=self.next_hashtags,
        )

        if next_page != False:
            yield get_next_tags_request

        hashtag_df = pd.DataFrame(self.result_lst)
        hashtag_df['owner_id'] = hashtag_df['owner_id'].astype('int64')
        hashtag_df['hashtag_name'] = hashtag_df['hashtag_name'].astype('category')
        hashtag_df.drop_duplicates(inplace=True)
        for ht in hashtag_df['hashtag_name'].unique():
            df_to_save = hashtag_df.loc[hashtag_df['hashtag_name'] == ht]
            results_hashtag_path = f'results/{ht}/{self.today_date}/'
            if not os.path.exists(results_hashtag_path):
                os.makedirs(results_hashtag_path)
            df_to_save.to_csv(f'{results_hashtag_path}{ht}.csv', index=True, header=True)

    