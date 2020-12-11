# -*- coding: utf-8 -*-
"""

"""

import requests

site = requests.get('https://austin.craigslist.org/search/fua?hasPic=1&postedToday=1&max_price=1000')
page_source = site.text


def getImages(page_source):
    for line in page_source:
        if "imgList" in line:
            return [c for c in line.split('\"') if 'https' in c]

site = requests.get('https://austin.craigslist.org/fuo/d/austin-black-tall-dresser/7245175921.html')
page_source = site.text.split('\n')
