# -*- coding:utf-8 -*-

from subprocess import call
import os
import time
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

while True:
    call(["scrapy", "crawl", "manga_fgo3"], cwd=dir_path)
    print('run crawler')
    time.sleep(3600)
