# -*- coding: utf-8 -*-
import logging
import re
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http import Request, FormRequest
from Github.items import UserItem, RepositoriesItem
try:
    import urlparse as parse
except:
    from urllib import parse

logger = logging.getLogger('Gitlogger')


class GithubSpider(Spider):
    name = 'github'
    allowed_domains = ['github.com']
    # redis_key = "userinfo:start_urls"
    start_urls = ['https://github.com/elvissong/following']
    HOST = 'https://github.com'
    custom_settings = {
        'COOKIES_ENABLED': True
    }
    crawl_ID = set()  # 待爬取用户
    finished_ID = set()  # 已爬取用户

    post_headers = {
        "HOST": "github.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
        "Referer": "https://github.com/",
    }

    def translate_str(self, numstr):
        num = str(numstr).strip().replace('.', '')
        if num.endswith('k'):
            num = int(num[:-1] + '000')
            return num
        elif num.endswith('M'):
            num = int(num[:-1]+'000000')
            return num
        else:
            return int(num)

    def start_requests(self):
        return [Request(url='https://github.com/login',headers=self.post_headers, callback=self.login)]

    def login(self, response):
        response_text = Selector(response)
        authenticity_token = response_text.xpath('//div[@id="login"]/form/div[1]/input[2]/@value').extract_first("")
        # match_obj = re.match('.*name="authenticity_token" type="hidden" value="(.*?)"', response_text, re.DOTALL)
        # authenticity_token = ''
        # if match_obj:
        #     authenticity_token = (match_obj.group(1))
        if authenticity_token:
            post_url = "https://github.com/session"
            post_data = {
            "commit": "Sign in",
            "utf8": '✓',
            "authenticity_token": authenticity_token,
            "login": "lyggnsxw@sina.cn",
            "password": "song19940325+",
            }

            return [FormRequest(
                url= post_url,
                formdata= post_data,
                headers= self.post_headers,
                callback= self.check_login)]

    def check_login(self, response):
        # 验证服务器返回数据是否登录成功
        if 200 <= response.status <300 :
            for url in self.start_urls:
                yield Request(url=url, dont_filter=True, headers=self.post_headers)

    def parse(self, response):
        resp = Selector(response)
        following_list = resp.xpath('//li[@class="follow-list-item float-left border-bottom"]/div/a/@href').extract()
        for elme in following_list:
            id = str(elme)[1:].lower()
            if id not in self.finished_ID and self.crawl_ID.__len__() <100:
                self.crawl_ID.add(id)
                yield Request(url='https://github.com/'+id,headers=self.post_headers, callback=self.parse_user,dont_filter=True)
                yield Request(url='https://github.com/'+id+'/repositories', headers=self.post_headers, callback=self.parse_user_repos, dont_filter=True)

        if self.crawl_ID.__len__() :
            id = self.crawl_ID.pop()
            self.finished_ID.add(id)
            next_url = "https://github.com/{0}/following".format(id)
            yield Request(url=next_url,headers=self.post_headers,callback=self.parse)

    def parse_user(self, response):
        """获取个人信息"""
        resp = Selector(response)
        useritem = UserItem()
        useritem['user_id'] = resp.xpath('//span[@class="vcard-username d-block"]/text()').extract_first("")
        nickname = resp.xpath('//span[@class="vcard-fullname d-block"]/text()').extract_first("")
        organization = resp.xpath('//li[@aria-label="Organization"]/div/text()').extract_first("")
        location = resp.xpath('//li[@aria-label="Home location"]/text()').extract_first("")
        email = resp.xpath('//li[@aria-label="Email"]/a/text()').extract_first("")
        blog = resp.xpath('//li[@aria-label="Blog or website"]/a/text()').extract_first("")
        user_repo_num = resp.xpath('//nav[@class="underline-nav"]/a[2]/span/text()').extract_first("")
        user_stars_num = resp.xpath('//nav[@class="underline-nav"]/a[3]/span/text()').extract_first("")
        user_followers_num = resp.xpath('//nav[@class="underline-nav"]/a[4]/span/text()').extract_first("")
        user_following_num = resp.xpath('//nav[@class="underline-nav"]/a[5]/span/text()').extract_first("")

        useritem['user_url'] = response.url
        useritem['user_nickname'] = nickname.strip()
        useritem['user_organization'] = organization.strip()
        useritem['user_location'] = location.strip()
        useritem['user_email'] = email.strip()
        useritem['user_blog'] = blog.strip()
        useritem['user_repo_num'] = self.translate_str(user_repo_num)
        useritem['user_stars_num'] = self.translate_str(user_stars_num)
        useritem['user_followers_num'] = self.translate_str(user_followers_num)
        useritem['user_following_num'] = self.translate_str(user_following_num)
        yield useritem

    def parse_user_repos(self, response):
        response = Selector(response)
        repos_urls = response.css('h3 a::attr(href)').extract()
        for url in repos_urls:
            full_url = self.HOST + url
            Request(url=full_url, headers=self.post_headers, callback=self.parse_repository)
        next_url = response.xpath('//div[@class="pagination"]/a[@rel="next"]/@href').extract_first()
        if next_url:
            full_next_url = 'https://github.com' + next_url
            yield Request(url=full_next_url, headers=self.post_headers, callback=self.parse_user_repos)
        else:
            pass

    def parse_repository(self, response):
        repoitem = RepositoriesItem()
        resp = Selector(response)
        # //*[@id="js-repo-pjax-container"]/div[1]/div[1]/h1/strong/a
        repo_name = resp.xpath('//h1[@class="public "]/strong/a/text()').extract_first("")
        # //*[@id="js-repo-pjax-container"]/div[1]/div[1]/h1/span[1]
        repo_owner_id = resp.xpath('//h1[@class="public "]/span[@class="author"]/text()').extract_first()
        # //*[@id="js-repo-pjax-container"]/div[1]/div[1]/h1/span[3]/span/a
        repo_is_forked = resp.xpath('//h1[@class="public "]/span[@class="fork-flag"]/span/a/text()').extract_first("")
        # //*[@id="js-repo-pjax-container"]/div[2]/div[1]/div[3]/span[1]
        repo_language = resp.xpath('//div[@class="repository-lang-stats-graph js-toggle-lang-stats"]/span/text()').extract_first()
        # //*[@id="js-repo-pjax-container"]/div[1]/div[1]/ul/li[3]/a
        repo_fork_num = resp.xpath('//ul[@class="pagehead-actions"]/li[3]/a/text()').extract_first("0")
        # //*[@id="js-repo-pjax-container"]/div[2]/div[1]/div[1]/div/div/span
        repo_desc = resp.xpath('//div[@class="repository-meta-content col-11 mb-1"]/span/text()').extract()
        # //*[@id="js-repo-pjax-container"]/div[1]/div[1]/ul/li[2]/div/form[2]/a
        repo_star_num = resp.xpath('//ul[@class="pagehead-actions"]/li[2]/div/form/a/text()').extract_first()
        #
        repo_tags = resp.xpath('//div[@class="topics-list-container"]/div/a/text()').extract()
        repo_url = response.url
        # //*[@id="js-repo-pjax-container"]/div[2]/div[1]/div[5]/span[1]/span/relative-time
        repo_last_update = resp.xpath('//span[@itemprop="dateModified"]/relative-time/@datatime').extract_first()
        yield repoitem
