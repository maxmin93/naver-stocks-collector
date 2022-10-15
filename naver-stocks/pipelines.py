# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import re

import pymongo
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem, NotConfigured


class StockGroupPipeline:
    def process_item(self, item, spider):
        row = ItemAdapter(item)
        row["grp_url"] = re.sub(r"\s", "", row["grp_url"])
        row["grp_name"] = re.sub(r"\s", "", row["grp_name"])
        row["vart_rate"] = re.sub(r"\s", "", row["vart_rate"]).replace("%", "")

        # validate
        if not row["grp_url"] or not row["grp_name"] or not row["vart_rate"]:
            raise DropItem(f"Empty string values in {row}")

        try:
            row["vart_rate"] = float(row["vart_rate"])
            row["stck_cnt"] = int(row["stck_cnt"])
            row["incr_cnt"] = int(row["incr_cnt"])
            row["flat_cnt"] = int(row["flat_cnt"])
            row["desc_cnt"] = int(row["desc_cnt"])
        except ValueError:
            raise DropItem(f"Wrong value as number type in {row}")

        if row["stck_cnt"] == 0:
            row["stck_cnt"] = row["incr_cnt"] + row["flat_cnt"] + row["desc_cnt"]

        return item


class MongoDBPipeline(object):
    def open_spider(self, spider):
        if (
            not spider.settings["MONGODB_SERVER"]
            or not spider.settings["MONGODB_DB"]
            or not spider.settings["MONGODB_COLLECTION"]
        ):
            raise NotConfigured("Missing MONGODB variables in settings")

        connection = pymongo.MongoClient(
            spider.settings["MONGODB_SERVER"], spider.settings.get("MONGODB_PORT", 27017)
        )
        db = connection[spider.settings["MONGODB_DB"]]
        self.collection = db[spider.settings["MONGODB_COLLECTION"]]

    def close_spider(self, spider):
        if self.collection:
            self.collection.database.client.close()
            self.collection = None
