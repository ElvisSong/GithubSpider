# -*- coding: utf-8 -*-
from scrapy.spiders import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.loader import ItemLoader
from Github.items import CommitItem


class CommitSpider(BaseSpider):
    # 定义spider名称
    name = "commit"
    allowed_domain = ['github.com']
    # 起始url地址
    start_urls = ['https://github.com/tensorflow/tensorflow/commits/master']

    # 处理函数
    def parse(self,response):
        resp = Selector(response)
        # 获取所有commit列表
        commit_list = resp.xpath('//div[@class="table-list-cell"]/p/a[@class="message"]/@href').extract()
        # 获取每个commit具体地址并构建合法url，使用回调函数处理commit
        for commit in commit_list:
            full_url = 'https://github.com' + commit
            yield Request(url=full_url, callback=self.parse_commit)
        # 获取下一页commit url 如果存在，则继续调用本函数进行提取
        next_page = resp.xpath('//div[@class="pagination"]/a/@href').extract_first()
        if next_page:
            full_next_page_url = 'https://github.com' + next_page
            yield Request(url=full_next_page_url, callback=self.parse)

    def parse_commit(self, response):
        resp = Selector(response)
        commititem = CommitItem()

        # 从页面中提取具体 commit 信息，如作者，时间，增删情况
        author = resp.xpath('//span[@class="commit-author-section"]/a[@class="user-mention"]/text()').extract_first()
        commit_date = resp.xpath('//span[@class="commit-author-section"]/relative-time/@datetime').extract_first()
        commit_stats = resp.xpath('//div[@id="toc"]/div[@class="toc-diff-stats"]/strong/text()').extract()
        # 对stats 进行处理，提取处增加和删除数据
        if commit_stats:
            commit_additions = commit_stats[0][:-9]
            commit_deletions = commit_stats[1][:-9]
            commit_additions = commit_additions.replace(',', '')
            commit_deletions = commit_deletions.replace(',', '')
            commit_changes = int(commit_additions) + int(commit_deletions)

        # 如果提取到正确数据，将数据存入item
        if author:
            commititem["author"] = author
        if commit_date:
            commititem["commit_date"] = commit_date
        if commit_stats:
            commititem["commit_changes"] = commit_changes
            commititem["commit_additions"] = int(commit_additions)
            commititem["commit_deletions"] = int(commit_deletions)

        yield commititem
