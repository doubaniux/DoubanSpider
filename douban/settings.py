# -*- coding: utf-8 -*-

# Scrapy settings for douban project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'douban'

SPIDER_MODULES = ['douban.spiders']
NEWSPIDER_MODULE = 'douban.spiders'

DUPEFILTER_DEBUG = False
# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'douban (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 0
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Host': 'book.douban.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:70.0) Gecko/20100101 Firefox/70.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    #'Cookie': 'bid=uJqh6AOxbMQ; douban-fav-remind=1; __utma=30149280.55746826.1572577334.1573517700.1573524975.12; __utmz=30149280.1572577334.1.1.utmcsr=bing|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); ll="118124"; gr_user_id=1726be90-a60e-4e97-8ce1-e044cad3617f; _vwo_uuid_v2=D8C2CAAC511C30838C970EBE9083C1D2B|dff8f1e50921397b98c19f14da75eaff; _pk_ref.100001.3ac3=%5B%22%22%2C%22%22%2C1573524974%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D; _pk_id.100001.3ac3=524e8ad2bcf516ff.1572849455.8.1573525114.1573518276.; __utma=81379588.1024998882.1572849456.1573518175.1573524975.8; __utmz=81379588.1573518175.7.4.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __yadk_uid=6jWdnb0y9C8NkHqAURbSUESMPn30pX7P; viewed="25862578_34721400_10763902_1084336_34866821_33440205_1148282_34809080_33436278"; __gads=Test; ct=y; __utmc=30149280; ap_v=0,6.0; __utmc=81379588; _pk_ses.100001.3ac3=*; __utmb=30149280.2.10.1573524975; __utmt_douban=1; __utmb=81379588.2.10.1573524975; __utmt=1',
    'DNT': '1',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'douban.middlewares.DoubanSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    #'douban.middlewares.RandomProxyMiddleware': 95,
    'douban.middlewares.SimpleProxyMiddleware': 100,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 105,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.throttle.AutoThrottle': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'douban.pipelines.BookPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 1
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 3
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# seems like 1 is the best value uising SimpleProxyMiddleware
AUTOTHROTTLE_TARGET_CONCURRENCY = 16
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = True
AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

FEED_EXPORT_ENCODING = 'utf-8'

# API that returns proxy address
# note that also the json key in middlewares.py need to be altered according to your API
PROXY_API = "http://127.0.0.1:5010/get/"
# static prxoy address
PROXY_URL = "http://username:password@yourproxyaddress:port"
# luminati proxy
BASE_PROXY_URL = "http://lum-customer-%(username)s-zone-static-country-%(country)s-session-%(session_id)s:%(password)s@zproxy.lum-superproxy.io:22225"

DOWNLOAD_TIMEOUT = 15