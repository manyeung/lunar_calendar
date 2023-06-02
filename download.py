from io import TextIOWrapper
import re
import urllib
import urllib.request
import os
import time
import json
import shutil
from log import log
from config import REQUEST_SLEEP, JSON_DIR, TEMP_DIR

def makeDays(file: TextIOWrapper, prevYear = None):
    beforeLunarJanuary = True
    year = None

    count = 0
    days = []

    for line in file:
        if count == 0:
            try:
                year = re.search(r'\([^\)]+\)', line)[0][1:-1]
                year = year.replace(' ', '')
            except:
                year = None
        else:
            if (re.search(r'\d{4}年\d{1,2}月\d{1,2}日', line)):
                arr = re.split(r'\s+', line.strip())

                if arr[1] == '正月':
                    beforeLunarJanuary = False

                date = arr[0]
                date = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date)
                date = '%04d-%02d-%02d' % (int(date[1]), int(date[2]), int(date[3]))

                days.append({
                    'date': date,
                    'lunar_day': arr[1],
                    'day_of_week': arr[2],
                    'terms': arr[3] if len(arr) > 3 else None,
                    'lunar_year': prevYear if beforeLunarJanuary else year,
                })

        count += 1

    return [days, year]

def download():
    shutil.rmtree(JSON_DIR, ignore_errors=True)
    os.mkdir(JSON_DIR)
    shutil.rmtree(TEMP_DIR, ignore_errors=True)
    os.mkdir(TEMP_DIR)

    year = '庚子-肖鼠' # 1900
    sleep = REQUEST_SLEEP

    # 1901 - 2100
    for y in range(1901, 2101):
        try:
            url = 'https://www.hko.gov.hk/tc/gts/time/calendar/text/files/T%sc.txt' % (y)
            fileTxt = '%s/%s.txt' % (TEMP_DIR, y)
            log('Downloading %s -> %s' % (url, fileTxt))
            urllib.request.urlretrieve(url, fileTxt)

            f = open(fileTxt, 'r', encoding='big5')
            [days, year] = makeDays(f, year)
            f.close()

            if year == None and y == 2058:
                year = '戊寅-肖虎'

                for d in days:
                    d['lunar_year'] = d['lunar_year'] if d['lunar_year'] else year

            json_formatted_str = json.dumps(days)
            fileJson = '%s/%s.json' % (JSON_DIR, y)
            f2 = open(fileJson, 'w')
            f2.write(json_formatted_str)
            f2.close()
            log('Wrote %s' % (fileJson))

            os.remove(fileTxt)
            log('Removed %s' % (fileTxt))
            log('Done')

            log('Wait for %ss for next request' % (sleep))
            time.sleep(sleep)
        except Exception as e:
            log('Error: %s, Year: %s' % (e, y))