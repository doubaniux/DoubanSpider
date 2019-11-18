# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class IsbnItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    isbn = scrapy.Field()


class BookItem(scrapy.Item):
    title = scrapy.Field()
    subtitle = scrapy.Field()
    orig_title = scrapy.Field()
    author = scrapy.Field()
    translator = scrapy.Field()
    language = scrapy.Field()
    pub_house = scrapy.Field()
    pub_date = scrapy.Field()
    pub_year = scrapy.Field()
    pub_month = scrapy.Field()
    binding = scrapy.Field()
    price = scrapy.Field()
    pages = scrapy.Field()
    isbn = scrapy.Field()
    other = scrapy.Field()
    img_url = scrapy.Field()