# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re
import pytz, datetime, calendar

class MangaFgo3Spider(CrawlSpider):
    name = 'manga_fgo3'
    allowed_domains = ['www.fate-go.jp']
    start_urls = ['http://www.fate-go.jp']

    rules = (
        Rule(LinkExtractor(allow='/manga_fgo3/$'), callback='parse_manga'),
    )

    def parse_manga(self, response):
        i = {}
        i['count'] = len(response.xpath('//body/div/div/div/ul/li/a[contains(@href,"comic")]/@href'))
        tz = pytz.timezone("Asia/Tokyo")
        now = datetime.datetime.now(tz)
        i['updated_at'] = i['created_at'] = calendar.timegm(now.utctimetuple())

        yield i
