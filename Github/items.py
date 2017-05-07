# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class GithubItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class UserItem(Item):
    user_id = Field()
    user_nickname = Field()
    user_url = Field()
    user_organization = Field()
    user_location = Field()
    user_blog = Field()
    user_email = Field()
    user_repo_num = Field()
    user_following_num = Field()
    user_followers_num = Field()
    user_stars_num = Field()


class RepositoriesItem(Item):
    repo_name = Field()
    repo_owner_id = Field()
    repo_is_forked = Field()
    repo_language = Field()
    repo_fork_num = Field()
    repo_desc = Field()
    repo_star_num = Field()
    repo_tags = Field()
    repo_url = Field()
    repo_last_update = Field()


class CommitItem(Item):
    author = Field()
    commit_date = Field()
    commit_changes = Field()
    commit_additions = Field()
    commit_deletions = Field()