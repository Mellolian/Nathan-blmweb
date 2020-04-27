# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# import json
# import time
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# CREDENTIALS_FILE = ''
# spreadsheet_id = '1uMAyc5gCKI8j2Z4SmHuY8_dQCW8CUMD1OK3EOb7mDpA'  # Alex' table
# scope = ['https://spreadsheets.google.com/feeds',
#          'https://www.googleapis.com/auth/drive']
# creds = ServiceAccountCredentials.from_json_keyfile_name('HAS.json', scope)
# client = gspread.authorize(creds)
# gc = gspread.authorize(creds)

# # Open a sheet from a spreadsheet in one go
# wks = gc.open("Nathan").sheet1
# wks.update('A2', article)
# Update a range of cells using the top left corner address
# wks.update('A2', [[1, 2], [3, 4]])


class JsonWriterPipeline(object):
    def open_spider(self, spider):
        self.file = open('shutterstock_rankings.json', 'w')
        self.file.write("[")

    def close_spider(self, spider):
        self.file.write("]")
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(
            dict(item),
            indent=4,
            sort_keys=True,
            separators=(',', ': ')
        ) + ",\n"
        self.file.write(line)
        return item
