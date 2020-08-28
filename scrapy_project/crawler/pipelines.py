# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import re
from datetime import datetime, timedelta

class CrawlerPipeline(object):
    def process_item(self, item, spider):
        # get current time and subtract the difference
        now = datetime.now()
        post_time = item['post_time'].replace('Online: ', '')
        # cases for days, minutes etc
        if re.match('[0-9]{2}\.[0-9]{4}\.[0-9]{2}', post_time):
            post_time = datetime.strptime(post_time, '%d.%m.%Y')
        elif re.search('[Tt]ag', post_time):
            number_days  = re.search('[0-9]+', post_time).group()
            post_time = now - timedelta(days=int(number_days))
        elif re.search('[Ss]tunde', post_time):
            number_hours  = re.search('[0-9]+', post_time).group()
            post_time = now - timedelta(days=int(number_hours))
        elif re.search('[Mm]inute', post_time):
            number_mins  = re.search('[0-9]+', post_time).group()
            post_time = now - timedelta(days=int(number_mins))
        else:
            post_time = None
        item['post_time'] = post_time

        return item
