# -*- coding: utf-8 -*-
"""

"""

import requests
from html.parser import HTMLParser

class Listing:
    def __init__(self, post_id):
        self.post_id = post_id

    def __str__(self):
        return f'Post ID: {self.post_id}, URL: {self.url}, Title: {self.title}, Time: {self.time}, ${self.price}'

class SearchParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.listings = []
        self.listing = None
        self.is_price = False
        self.is_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'li' and 'class' in attrs and attrs['class'] == 'result-row':
            self.listing = Listing(int(attrs['data-pid']))
        elif self.listing is not None:
            if tag == 'a':
                if not hasattr(self.listing, 'url'):
                    self.listing.url = attrs['href']
                elif 'result-title' in attrs['class']:
                    self.is_title = True
            elif tag == 'time':
                self.listing.time = attrs['datetime']
            elif tag == 'span' and attrs['class'] == 'result-price':
                self.is_price = True

    def handle_data(self, data):
        if self.is_title:
            self.listing.title = data
            self.is_title = False
        if self.is_price:
            self.listing.price = int(data[1:].replace(',',''))
            self.is_price = False

    def handle_endtag(self, tag):
        if self.listing is not None and tag == 'li':
            for listing in self.listings:
                if listing.post_id == self.listing.post_id:
                    self.listing = None
            if self.listing is not None:
                self.listings.append(self.listing)
                self.listing = None

class PostParser(HTMLParser):
    SMALL_END = '50x50c.jpg'
    LARGE_END = '600x450.jpg'

    def __init__(self):
        super().__init__()
        self.imgs = []
        self.is_description = False
        self.description = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'img':
            url = attrs['src']
            if url.endswith(self.SMALL_END):
                url = url[:-len(self.SMALL_END)] + self.LARGE_END
            self.imgs.append(url)
        elif tag == 'section' and 'id' in attrs and attrs['id'] == 'postingbody':
            self.is_description = True

    def handle_data(self, data):
        if self.is_description and 'QR Code Link' not in data:
            self.description += data

    def handle_endtag(self, tag):
        if tag == 'section' and self.is_description:
            self.is_description = False


site = requests.get('https://austin.craigslist.org/search/fua?hasPic=1&postedToday=1&max_price=1000')
page_source = site.text

parser = SearchParser()
parser.feed(page_source)
for listing in parser.listings:
    print(str(listing))
    print('\n')

#site = requests.get('https://austin.craigslist.org/fuo/d/austin-black-tall-dresser/7245175921.html')
#page_source = site.text

#parser = PostParser()
#parser.feed(page_source)
#print(parser.imgs)
#print(parser.description)


