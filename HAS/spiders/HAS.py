import scrapy
import time
import re
from scrapy.http import TextResponse
import requests
from pprint import pprint
import gspread
from oauth2client.service_account import ServiceAccountCredentials


TAG_RE = re.compile(r'<[^>]+>')

STRING_RE = re.compile(r'^((\s?)-|>)((.*)(20(1|2)\d))')


def remove_tags(text):
    return TAG_RE.sub('', text)


class HASSpider(scrapy.Spider):
    name = "blmweb"

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36 OPR/67.0.3575.137',
    }

    index = 1

    def start_requests(self):

        url = 'http://www.bmlweb.org/nouveaute.html'
        yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        titles = []

        full_text = response.xpath('//td[3]').extract()

        for text in full_text:
            lines = text.split('<br>')
            for line in lines:
                raw_line = remove_tags(line).replace(
                    '\n', '').replace('\t', '')

                correct_line = (STRING_RE.findall(raw_line))
                if not correct_line:
                    continue

                if 'href="' in line:
                    url = line.split('href="')[1].split('"')[0]
                    comment['url'] = url

                online_data = correct_line[0][2].split('-')[-1]
                if '–' in online_data:
                    online_data = correct_line[0][2].split('–')[-1]
                comment['online_data'] = online_data

                raw_source = re.findall(r'(\(\w+\))', correct_line[0][2])
                source = ''
                if raw_source:
                    source = raw_source[-1]
                    title = correct_line[0][2].split(
                        ' - ')[0].split(source)[0]
                else:
                    title = correct_line[0][2].split(
                        ' - ')[0].split(online_data)[0]
                comment['title'] = title
                comment['source'] = source
