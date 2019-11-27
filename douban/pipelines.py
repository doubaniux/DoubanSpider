# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import re
import json
import logging
import psycopg2
import psycopg2.extras
from psycopg2.errors import UniqueViolation
from douban.definitions import CONFIG_DIR

class BookPipeline(object):

    def __init__(self):
        super().__init__()
        self.logger = logging.Logger(self.__class__.__name__)
        with open(os.path.join(CONFIG_DIR, 'postgres.json'), 'r', encoding='utf-8') as f:
            config = json.load(f)
        self.conn = psycopg2.connect(
            dbname=config['dbname'],
            user=config['user'],
            password=config['password'],
            host=config['host'],
            port=config['port']
        )
        # transaction isolation level, autocommit means no transaction
        # self.conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_UNCOMMITTED
        self.conn.autocommit = True
        psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)
        self.cur = self.conn.cursor()
        # used to extract numbers
        self.regex = re.compile(r"\d+\d*")

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
            item['isbn'] = None if not item['isbn'] else item['isbn']
            #item['other'] = None if not item['other'] else Json(item['other'])
            item['other'] = None if not item['other'] else item['other']
            item['pages'] = int(self.regex.findall(item['pages'])[0]) if self.regex.findall(item['pages']) else None

            # the day doesn't matter
            year_month_day = self.regex.findall(item['pub_date'])
            if len(year_month_day) in (2, 3):
                item['pub_year'] = int(year_month_day[0])
                item['pub_month'] = int(year_month_day[1])
            elif len(year_month_day) == 1:
                item['pub_year'] = int(year_month_day[0])
                item['pub_month'] = None
            elif len(year_month_day) == 0:
                item['pub_year'] = None
                item['pub_month'] = None
            else:
                self.logger.info(f"unexpected pub_date pattern: {item['pub_date']}")
            # simple year and month range validation
            if item['pub_year'] and item['pub_month'] and item['pub_year'] < item['pub_month']:
                item['pub_year'], item['pub_month'] = item['pub_month'], item['pub_year']
            item['pub_year'] = None if item['pub_year'] is not None and not item['pub_year'] in range(0, 3000) else item['pub_year']
            item['pub_month'] = None if item['pub_month'] is not None and not item['pub_month'] in range(1, 12) else item['pub_month']

            # for the sql string formatting below, pub_date must be removed
            del item['pub_date']
            table_name = 'book'
            sql = 'INSERT INTO %s (%s) VALUES (%%(%s)s );' % (table_name, ', '.join(item), ')s, %('.join(item))
            try:
                self.cur.execute(sql, dict(item))
                self.conn.commit()
            except UniqueViolation as e:
                pass

        return item

    def close_spider(self, spider):
        if spider.name == "book":
            self.cur.close()
            self.conn.close()
