# -*- coding: utf-8 -*-
"""

"""

import requests

#site = requests.get('https://austin.craigslist.org/search/fua?hasPic=1&postedToday=1&max_price=1000')
site = requests.get('https://austin.craigslist.org/fuo/d/austin-black-tall-dresser/7245175921.html')

page_source = site.text.split('\n')


def getImages(page_source):
    for line in page_source:
        if "imgList" in line:
            images = []
            for candidate in line.split('\"'):
                if 'https' in candidate:
                    images.add(candidate)
            return images