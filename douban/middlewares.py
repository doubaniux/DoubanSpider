# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import json
import os
import requests
import logging
import string
import random
from douban.definitions import CONFIG_DIR


class RandomProxyMiddleware:

    def __init__(self, settings):
        self.logger = logging.Logger(self.__class__.__name__)
        self.PROXY_API = settings.get('PROXY_API')
        if self.PROXY_API is None:
            raise KeyError('proxy API required')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def __get_proxy(self):
        self.logger.debug('acquiring proxy')
        proxy_addr = json.loads(requests.get(self.PROXY_API).text)['proxy']
        self.logger.debug("acquired proxy: " + proxy_addr)
        return proxy_addr

    def process_request(self, request, spider):
        chosen_proxy = self.__get_proxy()
        request.meta['proxy'] = "http://" + chosen_proxy
        self.logger.debug("using proxy: " + chosen_proxy)

    def process_response(self, request, response, spider):
        # better limit retry times
        if int(response.status) in [504, 408, 403, 400, 302, 301]:
            self.logger.error(f"Response status: {response.status} from {request.url}, retrying")
            return request
        if 'dataloss' in response.flags:
            return request
        return response

    def process_exception(self, request, exception, spider):
        self.logger.error(exception)
        self.logger.info(f"exception catched, retrying request to {request.url}")
        return request


class SimpleProxyMiddleware:
    def __init__(self, settings):
        self.logger = logging.Logger(self.__class__.__name__)
        self.proxy = settings.get('PROXY_URL')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        request.meta['proxy'] = self.proxy

    def process_response(self, request, response, spider):
        # better limit retry times
        if int(response.status) in [504, 408, 403, 400, 302, 301]:
            self.logger.error(f"Response status: {response.status} from {request.url}, retrying")
            return request
        if 'dataloss' in response.flags:
            return request
        return response

    def process_exception(self, request, exception, spider):
        self.logger.error(exception)
        self.logger.info(f"exception catched, retrying request to {request.url}")
        return request


class LuminatiProxyMiddleware:
    '''
    Use different IP per request, by adding random session id to the proxy url
    '''
    def __init__(self, settings):
        self.logger = logging.Logger(self.__class__.__name__)
        self.base_proxy = settings.get('BASE_PROXY_URL')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        request.meta['proxy'] = self.__acquire_proxy()

    def process_response(self, request, response, spider):
        # better limit retry times
        if int(response.status) in [504, 408, 403, 400, 302, 301]:
            self.logger.error(f"Response status: {response.status} from {request.url}, retrying")
            return request
        if 'dataloss' in response.flags:
            return request
        return response

    def process_exception(self, request, exception, spider):
        self.logger.debug(exception)
        self.logger.debug(f"exception catched, retrying request to {request.url}")
        return request

    def __acquire_proxy(self):
        with open(os.path.join(CONFIG_DIR, 'luminati.json')) as f:
            config = json.load(f)
        config['session_id'] = self.__generate_random_id()
        return self.base_proxy % config
    
    def __generate_random_id(self):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for i in range(random.randint(5,25)))
