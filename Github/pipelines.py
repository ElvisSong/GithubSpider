# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from settings import MONGO_DB, MONGO_PORT, MONGO_URI
from items import CommitItem, UserItem, RepositoriesItem


class GithubPipeline(object):
    def __init__(self):
        client = pymongo.MongoClient(MONGO_URI, MONGO_PORT)
        db = client[MONGO_DB]
        self.Commit = db["Commit"]
        self.User = db["User"]
        self.Repositories = db["Repositories"]

    def process_item(self, item, spider):
        if isinstance(item, CommitItem):
            try:
                self.Commit.insert(dict(item))
            except Exception as e:
                pass
        elif isinstance(item, UserItem):
            try:
                self.User.insert(dict(item))
            except Exception as e:
                pass
        elif isinstance(item, RepositoriesItem):
            try:
                self.Repositories.insert(dict(item))
            except Exception as e:
                pass
        return item

