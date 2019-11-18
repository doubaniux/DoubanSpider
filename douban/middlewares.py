# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

import json
import requests
import logging


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
