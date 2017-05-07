# -*- coding: utf-8 -*-
import json
from scrapy.spiders import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request
from Github.items import CommitItem


class TrendingSpider(BaseSpider):
    name = 'trending'
    allowed_domain = ['github.com']
    host = ['https://github.com']
    handle_httpstatus_list = [404, 403, 401]  # 如果返回这个列表中的状态码，爬虫也不会终止
    token = '7d3ea3e9e38771ffc7ef9397abe90af8406e76a0'
    num = 1

    def start_requests(self):
        start_urls = []
        url = "https://api.github.com/repos/tensorflow/tensorflow/commits?per_page=99&page=" + str(self.num)
        start_urls.append(url)
        for url in start_urls:
            yield Request(url, callback=self.parse)

    def parse(self, response):
        # resp = Selector(response)
        # self.repo_list = resp.xpath('//ol[@class="repo-list"]/li/div/h3/a/@href').extract()
        # for repo in self.repo_list:
        #     full_url = "https://api.github.com/repos" + repo + "/commits"
        #     yield Request(url=full_url, callback=self.parse_repo)
        if response.status in self.handle_httpstatus_list:
            self.num += 1

        commit_list = json.loads(response.body)

        if len(commit_list) == 99:
            self.num += 1
            for commit in commit_list:
                commit_url = commit["url"]
                yield Request(url=commit_url, callback=self.parse_commit)
        elif len(commit_list) < 99:
            for commit in commit_list:
                commit_url = commit["url"]
                yield Request(url=commit_url, callback=self.parse_commit)

    def parse_commit(self, response):
        print response.headers['X-RateLimit-Remaining']
        commititem = CommitItem()
        commit_detail = json.loads(response.body)
        if commit_detail:
            commititem['committer'] = commit_detail["commit"]["committer"]["name"]
            commititem['commit_date'] = commit_detail["commit"]["committer"]["date"]
            commititem['commit_changes'] = commit_detail["stats"]["total"]
            commititem['commit_additions'] = commit_detail["stats"]["additions"]
            commititem['commit_deletions'] = commit_detail["stats"]["deletions"]
        return commititem
