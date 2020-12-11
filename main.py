# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import requests

#site = requests.get('https://austin.craigslist.org/search/fua?hasPic=1&postedToday=1&max_price=1000')
site = requests.get('https://austin.craigslist.org/fuo/d/austin-black-tall-dresser/7245175921.html')

page_source = site.text.split('\n')


#When opening a specific listing
for line in page_source:
    if "imgList" in line:
        images = line.split('\"')
        for candidate in images:
            if 'https' not in candidate:
                print(candidate)
    
