from tabulate import tabulate
import os
import shutil
import json
import datetime
from config import JSON_DIR, HTML_DIR, TEMPLATE_PATH
from log import log

def makeTable(list: list):
    html = ''

    if not list:
        return html
    
    lastday = list[len(list)-1]
    lunar_year = lastday['lunar_year']
    year = lastday['date'][:4]
    month = int(lastday['date'][5:7])
    
    list = [
        "%s[br]%s[br]%s" % (int(d['date'][8:]), d['lunar_day'], d['terms'] if d['terms'] else '') if d else None
        for d in list
    ]

    table = []

    for i in range(0, len(list), 7):
        table.append(list[i:i+7])

    if table:
        html += '<h3>%s年%s月 %s</h3>' % (year, month, lunar_year)
        html += tabulate(table, headers=['一', '二', '三', '四', '五', '六', '日'], tablefmt="html", disable_numparse=True)

    return html.replace('[br]', '<br>')

def html():
    shutil.rmtree(HTML_DIR, ignore_errors=True)
    os.mkdir(HTML_DIR)

    f = open(TEMPLATE_PATH, 'r')
    template = f.read()
    f.close()

    for file in os.listdir(JSON_DIR):
        y = file[:4]

        f = open('%s/%s' % (JSON_DIR, file), 'r')
        days = json.load(f)
        f.close()

        list = []
        month = None

        table = ''

        for d in days:
            date = datetime.date.fromisoformat(d['date'])

            if date.month != month:
                table += makeTable(list)
                list.clear()

                weekday = date.weekday()
                for i in range(weekday):
                    list.append(None)

                month = date.month

            list.append(d)

        table += makeTable(list)
        list.clear()

        html = template.replace('{TITLE}', '%s年' % y).replace('{BODY}', table)

        fileHtml = '%s/%s.html' % (HTML_DIR, y)
        with open(fileHtml, 'w', encoding='utf-8') as f:
            f.write(html)
            log('Wrote %s' % fileHtml)