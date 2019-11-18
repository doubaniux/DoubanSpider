import scrapy
import os
import csv
import logging
import time
from scrapy.http import Request
from douban.items import BookItem
from douban.email import send_email
from douban.definitions import ROOT_DIR
from douban.definitions import CSV_DIR
from douban.definitions import HTML_DIR


class BookSpider(scrapy.Spider):
    name = "book"

    def start_requests(self):
        with open(os.path.join(ROOT_DIR, 'user_list.txt'), 'r', encoding='utf-8') as f:
            users = list(map(lambda x: x.strip(), f.readlines()))
        base_url = 'https://book.douban.com/people/'
        urls = list(map(lambda x: base_url + x + '/', users))
        # some buddy who has about 50 books marked, used for testing
        urls = ["https://book.douban.com/people/91014926/"]
    
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
                yield response.follow(list_page_url, self.parse_list, dont_filter=True,)
            
        except:
            self.log("parsing failed", level=logging.ERROR)
            html_file_name = (time.asctime() + 'count.html').replace(' ', '_').replace(':', '-')
            with open(os.path.join(HTML_DIR, html_file_name), 'w', encoding='utf-8') as f:
                f.write(response.text)
            with open(os.path.join(HTML_DIR, html_file_name), 'a', encoding='utf-8') as f:
                f.writelines(response.url)
                f.writelines(time.asctime())
            yield Request(response.url, callback=self.parse_home, dont_filter=True,)

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
            yield Request(response.url, callback=self.parse_list, dont_filter=True,)
        # there should be books on the page
        elif response.css('li.subject-item'):
            for book in response.css('li.subject-item'):
                detail_url = book.xpath('div[2]/h2/a/@href').get().strip()
                book_name = book.xpath('div[2]/h2/a/text()').get().strip()
                self.log(f"go to the detail page of book {book_name}")
                yield response.follow(detail_url, self.parse_detail, dont_filter=True,)
            # under some tags there is no paginator
            if response.css('.paginator'):
                next_page = response.css('.next a::attr(href)').get()
                # if hasn't reached the last page yet
                if next_page:
                    yield response.follow(next_page.strip(), self.parse_list, dont_filter=True,)
                else:
                    self.log(f"reached the end")
            else:
                self.log("no paginator in this page", level=logging.DEBUG)

    def parse_detail(self, response):
        # no title found
        if not response.xpath("/html/body/div[3]/h1/span/text()"):
            self.log("no title in this detail page", level=logging.ERROR)
            html_file_name = (time.asctime() + 'no_title.html').replace(' ', '_').replace(':', '-')
            with open(os.path.join(HTML_DIR, html_file_name), 'w', encoding='utf-8') as f:
                f.write(response.text)
            with open(os.path.join(HTML_DIR, html_file_name), 'a', encoding='utf-8') as f:
                f.writelines(response.url)
                f.writelines(time.asctime())
            yield Request(response.url, callback=self.parse_detail, dont_filter=True,)            
        else:
            title = response.xpath("/html/body/div[3]/h1/span/text()").get().strip()

            subtitle_elem = response.xpath("//div[@id='info']//span[text()='副标题:']/following::text()")
            subtitle = subtitle_elem.get().strip() if subtitle_elem else None

            orig_title_elem = response.xpath("//div[@id='info']//span[text()='原作名:']/following::text()")
            orig_title = orig_title_elem.get().strip() if orig_title_elem else None

            pub_house_elem = response.xpath("//div[@id='info']//span[text()='出版社:']/following::text()")
            pub_house = pub_house_elem.get().strip() if pub_house_elem else None

            pub_date_elem = response.xpath("//div[@id='info']//span[text()='出版年:']/following::text()")
            pub_date = pub_date_elem.get().strip() if pub_date_elem else None

            binding_elem = response.xpath("//div[@id='info']//span[text()='装帧:']/following::text()")
            binding = binding_elem.get().strip() if binding_elem else None

            price_elem = response.xpath("//div[@id='info']//span[text()='定价:']/following::text()")
            price = price_elem.get().strip() if price_elem else None

            pages_elem = response.xpath("//div[@id='info']//span[text()='页数:']/following::text()")
            pages = pages_elem.get().strip() if pages_elem else None

            isbn_elem = response.xpath("//div[@id='info']//span[text()='ISBN:']/following::text()")
            isbn = isbn_elem.get().strip() if isbn_elem else None

            img_url_elem = response.xpath("//*[@id='mainpic']/a/img/@src")
            img_url = img_url_elem.get().strip() if img_url_elem else None

            authors_elem = response.xpath("//div[@id='info']//span[text()=' 作者']/following-sibling::a/text()")
            if authors_elem:
                authors = []
                for author in authors_elem:
                    authors.append(author.get().strip())
            else:
                authors = None

            translators_elem = response.xpath("//div[@id='info']//span[text()=' 译者']/following-sibling::a/text()")
            if translators_elem:
                translators = []
                for translator in translators_elem:
                    translators.append(translator.get().strip())
            else:
                translators = None
            
            other = {}
            cncode_elem = response.xpath("//div[@id='info']//span[text()='统一书号:']/following::text()")
            if cncode_elem:
                other['cncode'] = cncode_elem.get().strip()
            series_elem = response.xpath("//div[@id='info']//span[text()='丛书:']/following-sibling::a/text()")
            if series_elem:
                other['series'] = series_elem.get().strip()            
            imprint_elem = response.xpath("//div[@id='info']//span[text()='出品方:']/following-sibling::a/text()")
            if imprint_elem:
                other['imprint'] = imprint_elem.get().strip()

            # language is expected to be filled by the data from worldcat.org
            # it is way too hassling access worldcat.org in China
            language = None

            book = BookItem(
                    title = title,
                    subtitle = subtitle,
                    orig_title = orig_title,
                    author = authors,
                    translator = translators,
                    language = language,
                    pub_house = pub_house,
                    pub_date = pub_date,
                    binding = binding,
                    price = price,
                    pages = pages,
                    isbn = isbn,
                    other = other,
                    img_url = img_url,
            )
            yield book

    def closed(self, reason):
        subject = f"Spider has stopped, reason:{reason}.\n"
        content = f"Spider has stopped at {time.asctime()}, reason:{reason}.\n"
        send_email(subject, content)
