import scrapy
import time
import re
import json
from scrapy.http import TextResponse
import requests
from pprint import pprint
import gspread
from google.oauth2.service_account import Credentials


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
        scopes = ['https://spreadsheets.google.com/feeds',
                  'https://www.googleapis.com/auth/drive']

        credentials = Credentials.from_service_account_file(
            'bmlweb-d5bced2a88c6.json', scopes=scopes)
        gc = gspread.authorize(credentials)
# Open a sheet from a spreadsheet in one go
        wks = gc.open("bmlweb").sheet1

        j = 1
        batch = []

        columns = response.xpath('//tr')
        for column in columns[2:]:
            left_column = column.xpath('.//td[1]').extract_first()
            text = column.xpath('.//td[3]').extract_first()

            if text:
                lines = text.split('<br>')
            articles = []
            for line in lines:
                comment = []
                comment.append(remove_tags(left_column))

                raw_line = remove_tags(line).replace(
                    '\n', '').replace('\t', '')

                if 'href="' in line:
                    url = line.split('href="')[1].split('"')[0]

                correct_line = (STRING_RE.findall(raw_line))
                if not correct_line:
                    continue

                online_date = correct_line[0][2].split('-')[-1]
                if '–' in online_date:
                    online_date = correct_line[0][2].split('–')[-1]

                raw_source = re.findall(r'(\(\w+\))', correct_line[0][2])
                source = ''
                if raw_source:
                    source = raw_source[-1].strip('(').strip(')')
                    title = correct_line[0][2].split(
                        ' - ')[0].split(source)[0]
                else:
                    title = correct_line[0][2].split(
                        ' - ')[0].split(online_date)[0]
                comment.append(title)
                comment.append('')
                comment.append('')
                comment.append(url)
                comment.append(source)
                comment.append(online_date)
                if title and url and source and online_date:
                    articles.append(comment)

            batch += articles
            articles = []
            if len(batch) > 900:
                print(len(batch))
                wks.batch_update([{
                    'range': f'A2:I{2+len(batch)}',
                    'values': batch,
                }])
                wks = gc.open("bmlweb").get_worksheet(j)
                j += 1
                batch = []
