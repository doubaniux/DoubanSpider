# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import re
import json
import psycopg2
from datetime import date
from psycopg2.extras import Json
from douban.definitions import CONFIG_DIR

class BookPipeline(object):

    def __init__(self):
        super().__init__()
        with open(os.path.join(CONFIG_DIR, 'postgres.json'), 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.conn = psycopg2.connect(
            dbname=config['dbname'],
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port']
        )
        # transaction isolation level, read uncommitted should be fine
        self.conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_UNCOMMITTED
        psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)
        self.cur = self.conn.cursor()
        # used to extract numbers
        self.regex = re.compile(r"\d+\.?\d*")

    def open_spider(self, spider):
        if spider.name != "book":
            del self.conn 
            del self.cur

    def process_item(self, item, spider):
        if spider.name == "book":
            # since major of fileds are char type, set each to empty string
            for k, v in item.items():
                item[k] = '' if not item[k] else item[k]
            # then handle the minority
            item['author'] = list() if not item['author'] else item['author']
            item['translator'] = list() if not item['translator'] else item['translator']
            # isbn is not nullable in the db, but sometimes only cncode is provided
            # this is not code level secured.
            item['isbn'] = item['other']['cncode'] if not item['isbn'] else item['isbn']
            #item['other'] = None if not item['other'] else Json(item['other'])
            item['other'] = None if not item['other'] else item['other']
            item['pages'] = int(self.regex.findall(item['pages'])[0]) if item['pages'] else None
            year_month_day = self.regex.findall(item['pub_date'])
            # the day doesn't matter
            if len(year_month_day) == 2:
                item['pub_year'] = int(year_month_day[0])
                item['pub_month'] = int(year_month_day[1])
            elif len(year_month_day) == 1:
                item['pub_year'] = int(year_month_day[0])
                item['pub_month'] = None
            elif len(year_month_day) == 0:
                item['pub_year'] = None
                item['pub_month'] = None                
            
            # for the sql string formatting below, pub_date must be removed
            del item['pub_date']
            table_name = 'book'
            sql = 'INSERT INTO %s (%s) VALUES (%%(%s)s );' % (table_name, ', '.join(item), ')s, %('.join(item))
            self.cur.execute(sql, dict(item))
            self.conn.commit()

        return item

    def close_spider(self, spider):
        if spider.name == "book":
            self.cur.close()
            self.conn.close()
