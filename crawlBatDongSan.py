#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 16:23:52 2021

@author: giang
"""

import logging
import re
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from itertools import chain
import pandas as pd
logger = logging.getLogger('Crawl BatDongSan')
import json
# import pydash

def gia_bat_dong_san(url):
    HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'referer': 'https://batdongsan.com.vn/',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',}
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'lxml')
    all_pages = soup.find('div', {'class': 'background-pager-right-controls'})
    avail_page = []
    for page in all_pages:
        if isinstance(page, NavigableString):
            continue
        if isinstance(page, Tag):
            page_url = page.get('href')
            try:
                MAIN = re.compile(r'/p(.*)')
                page_number = MAIN.search(page_url).group(1)
                avail_page.append(int(page_number))
            except Exception as e:
                logger.error(e)
    ret = []
    for i in range(1, avail_page[-1]+1):
        print('Getting data for page', url+'/p'+str(i))
        response_page = requests.get(url+'/p'+str(i), headers=HEADERS)
        soup_page = BeautifulSoup(response_page.content, 'lxml')
        SEARCH_PATTERN = re.compile(r'.*?search-productItem')
        posts = soup_page.find_all('div', {'class': SEARCH_PATTERN})
        each = []
        for item in posts:
            data = dict(
            title=item.find('div', attrs={'class': 'p-title'}).a.get('title'),
            description=item.find('div', attrs={'class': 'p-main-text'}).text,
            price=item.find('strong', attrs={'class': 'product-price'}).text,
            area=item.find('strong', attrs={'class': 'product-area'}).text,
            location=item.find('strong', attrs={'class': 'product-city-dist'}).text,
            )
            each.append(data)
        ret.append(each)
        df = pd.DataFrame(list(chain.from_iterable(ret)))
    return df