# -*- coding: utf-8 -*-
"""

"""

import requests
from html.parser import HTMLParser

site = requests.get('https://austin.craigslist.org/search/fua?hasPic=1&postedToday=1&max_price=1000')
page_source = site.text

class ImagesParser(HTMLParser):
    SMALL_END = '50x50c.jpg'
    LARGE_END = '600x450.jpg'
    def __init__(self):
        super().__init__()
        self.imgs = []

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            attrs = dict(attrs)
            url = attrs['src']
            if url.endswith(self.SMALL_END):
                url = url[:-len(self.SMALL_END)] + self.LARGE_END
            self.imgs.append(url)

site = requests.get('https://austin.craigslist.org/fuo/d/austin-black-tall-dresser/7245175921.html')
page_source = site.text

parser = ImagesParser()
parser.feed(page_source)
print(parser.imgs)


