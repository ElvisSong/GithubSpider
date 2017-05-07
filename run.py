# -*- coding: utf-8 -*-
from scrapy import cmdline

cmdline.execute('scrapy crawl github'.split())
# cmdline.execute('scrapy crawl trending'.split())
# cmdline.execute('scrapy crawl commit'.split())