'''
    For exprimental and testing purpose only.
'''
import scrapy
import os
import csv
import logging
import time
from scrapy.http import Request
from douban.items import IsbnItem
from douban.email import send_email
from douban.definitions import ROOT_DIR
from douban.definitions import CSV_DIR
from douban.definitions import HTML_DIR


class ISBNSpider(scrapy.Spider):
    # handle_httpstatus_list = [301, 302]
    name = 'isbn'

    def start_requests(self):
        urls = [
            'https://book.douban.com/tag/',
        ]
        f = open(os.path.join(CSV_DIR, 'books.csv'), 'w', newline='', encoding='utf-8')
        f.close()
        f = open(os.path.join(CSV_DIR, 'isbn.csv'), 'w', newline='', encoding='utf-8')
        f.close()
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_tag,
                dont_filter=True,
            )

    def parse_tag(self, response):
        # self.log('start', level=logging.INFO)
        for tag in response.css(".tagCol a"):
            tag_name = tag.css("::text").get().strip()
            tag_url = tag.css("::attr(href)").get().strip()
            self.log(f"go to {tag_name} page")
            # go to the list page of each tag
            yield response.follow(tag_url, self.parse_list, dont_filter=True,)

    def parse_list(self, response):
        # if no logo found, that means the request is blocked
        if not response.css('.nav-logo'):
            self.log(
                f"failed to load website logo at {response.url}, retrying request",
                level=logging.DEBUG
            )
            yield Request(response.url, callback=self.parse_list, dont_filter=True,)
        # there should be books on the page
        elif response.css('li.subject-item'):
            for book in response.css('li.subject-item'):
                detail_url = book.xpath('div[2]/h2/a/@href').get().strip()
                book_name = book.xpath('div[2]/h2/a/text()').get().strip()
                self.log(f"go to the detail page of book {book_name}")
                yield response.follow(detail_url, self.parse_isbn, dont_filter=True,)
            # under some tags there is no paginator
            if response.css('.paginator'):
                next_page = response.css('.next a::attr(href)').get()
                # if hasn't reached the last page yet
                if next_page:
                    yield response.follow(next_page.strip(), self.parse_list, dont_filter=True,)
                else:
                    tag = response.xpath('/html/body/div[3]/div[1]/h1/text()').get().strip()
                    self.log(f"reached the end of tag {tag}")
            else:
                self.log("no paginator on this page")

    def parse_isbn(self, response):
        try:
            # if the detail page loaded correctly, this should work
            title = response.xpath("/html/body/div[3]/h1/span/text()").get().strip()
            isbn = response.xpath("//*[@id='info']/text()")[-2].get().strip()
            self.log(f'now at the detial page of book {title}')
            book = IsbnItem(title=title, isbn=isbn)
            yield book
            with open(os.path.join(CSV_DIR, 'books.csv'), 'a+', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow([title, isbn])
                self.log(f"recorded the title of {title}")
            with open(os.path.join(CSV_DIR, 'isbn.csv'), 'a+', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow([isbn, ])
                self.log(f"recorded the isbn of {title}")
        except:
            # if failed then retry
            self.log(f"error occured at isbn page, retrying request to {response.url}", level=logging.DEBUG)
            yield Request(response.url, callback=self.parse_isbn, dont_filter=True,)

    def closed(self, reason):
        subject = f"Spider has stopped, reason:{reason}.\n"
        content = f"Spider has stopped at {time.asctime()}, reason:{reason}.\n"
        send_email(subject, content)


class TestSpider(scrapy.Spider):
    name = 'test'

    def start_requests(self):
        urls = [
            'https://book.douban.com/people/xinqiaoju/wish',
        ]
        f = open(os.path.join(CSV_DIR, 'test.csv'), 'w', newline='', encoding='utf-8')
        f.close()
        self.item_count = 0
        self.item_expected = 4427
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_list,
                dont_filter=True,
            )

    def parse_list(self, response):
        if not response.css('.nav-logo'):
            self.log(
                f"failed to load website logo at {response.url}, retrying request",
                level=logging.ERROR
            )
            with open(os.path.join(HTML_DIR, 'no_logo.html'), 'w', encoding='utf-8') as f:
                f.write(response.text)
            with open(os.path.join(HTML_DIR, 'no_logo.html'), 'a', encoding='utf-8') as f:
                f.writelines(response.url)
                f.writelines(time.asctime())
            yield Request(response.url, callback=self.parse_list, dont_filter=True,)
        # there should be books on the page
        elif response.css('li.subject-item'):
            for book in response.css('li.subject-item'):
                detail_url = book.xpath('div[2]/h2/a/@href').get().strip()
                book_name = book.xpath('div[2]/h2/a/text()').get().strip()
                self.log(f"go to the detail page of book {book_name}")
                yield response.follow(detail_url, self.parse_isbn, dont_filter=True,)
            # under some tags there is no paginator
            if response.css('.paginator'):
                next_page = response.css('.next a::attr(href)').get()
                # if hasn't reached the last page yet
                if next_page:
                    yield response.follow(next_page.strip(), self.parse_list, dont_filter=True,)
                else:
                    self.log(f"reached the end")
            else:
                self.log("no paginator in this page", level=logging.INFO)

    def parse_isbn(self, response):
        try:
            # if the detail page loaded correctly, this should work
            title = response.xpath("/html/body/div[3]/h1/span/text()").get().strip()
            isbn = response.xpath("//*[@id='info']/text()")[-2].get().strip()
            self.log(f'now at the detial page of book {title}')
            book = IsbnItem(title=title, isbn=isbn)
            yield book
            self.item_count += 1
            with open(os.path.join(CSV_DIR, 'test.csv'), 'a+', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow([title, isbn])
                self.log(f"recorded the title of {title}")
        except:
            # if failed then retry
            self.log(f"error occured at isbn page, retrying request to {response.url}", level=logging.ERROR)
            with open(os.path.join(HTML_DIR, 'no_detail.html'), 'w', encoding='utf-8') as f:
                f.write(response.text)
            with open(os.path.join(HTML_DIR, 'no_detail.html'), 'a', encoding='utf-8') as f:
                f.writelines(response.url)
                f.writelines(time.asctime())
            yield Request(response.url, callback=self.parse_isbn, dont_filter=True,)

    def closed(self, reason):
        subject = f"Spider has stopped, reason:{reason}.\n"
        content = f"Spider has stopped at {time.asctime()}, reason:{reason}.\n"
        send_email(subject, content)


class BookCountingSpider(scrapy.Spider):
    name = 'count'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = set()
        self.regex = re.compile(r"\d+\d*")

    def start_requests(self):
        with open(os.path.join(ROOT_DIR, 'user_list.txt'), 'r', encoding='utf-8') as f:
            users = list(map(lambda x: x.strip(), f.readlines()))
        base_url = 'https://book.douban.com/people/'
        urls = list(map(lambda x: base_url + x + '/', users))

        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_home,
                dont_filter=True,
            )

    def parse_home(self, response):
        try:
            # go to do/collect/wish list page
            for list_page in response.xpath('//*[@id="db-book-mine"]//h2//a/@href'):
                list_page_url = list_page.get().strip()
                yield response.follow(list_page_url, self.parse_list, dont_filter=True, )

        except:
            self.log("parsing failed", level=logging.ERROR)
            html_file_name = (time.asctime() + 'count.html').replace(' ', '_').replace(':', '-')
            with open(os.path.join(HTML_DIR, html_file_name), 'w', encoding='utf-8') as f:
                f.write(response.text)
            with open(os.path.join(HTML_DIR, html_file_name), 'a', encoding='utf-8') as f:
                f.writelines(response.url)
                f.writelines(time.asctime())
            yield Request(response.url, callback=self.parse_home, dont_filter=True, )

    def parse_list(self, response):
        if not response.css('.nav-logo'):
            self.log(
                f"failed to load website logo at {response.url}, retrying request",
                level=logging.ERROR
            )
            html_file_name = (time.asctime() + 'no_logo.html').replace(' ', '_').replace(':', '-')
            with open(os.path.join(HTML_DIR, html_file_name), 'w', encoding='utf-8') as f:
                f.write(response.text)
            with open(os.path.join(HTML_DIR, html_file_name), 'a', encoding='utf-8') as f:
                f.writelines(response.url)
                f.writelines(time.asctime())
            yield Request(response.url, callback=self.parse_list, dont_filter=True, )
        # there should be books on the page
        elif response.css('li.subject-item'):
            for book in response.css('li.subject-item'):
                detail_url = book.xpath('div[2]/h2/a/@href').get().strip()
                subject_number = int(self.regex.findall(detail_url)[0])
                self.counter.add(subject_number)
                # with open(os.path.join(ROOT_DIR, 'count.log'),'w') as fp:
                    # fp.write(str(len(self.counter)))
            # under some tags there is no paginator
            if response.css('.paginator'):
                next_page = response.css('.next a::attr(href)').get()
                # if hasn't reached the last page yet
                if next_page:
                    yield response.follow(next_page.strip(), self.parse_list, dont_filter=True, )
                else:
                    self.log(f"reached the end")
            else:
                self.log("no paginator in this page", level=logging.DEBUG)

    def closed(self, reason):
        total = len(self.counter)
        msg = f"{total} books in total."
        self.log(msg, level=logging.INFO)
        send_email("book counting has finished.", msg)

