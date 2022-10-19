# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json

import pymongo
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem, NotConfigured


class StockItemPipeline:
    def open_spider(self, spider):
        if spider.settings.get("ITEM_LIST_OUTPUT") is None:
            raise NotConfigured("ITEM_LIST_OUTPUT is not set")
        self.file = open(spider.settings.get("ITEM_LIST_OUTPUT"), "w", encoding="utf-8")

    def close_spider(self, spider):
        self.file.close()

    def _info(self, item):
        return {
            "stck_name": item["stck_name"],
            "stck_url": item["stck_url"],
        }

    def process_item(self, item, spider):
        row = ItemAdapter(item)

        # validate
        if not row["stck_url"] or not row["stck_name"] or not row["prdy_ctrt"]:
            raise DropItem(f"Empty string values in {row}")

        line = json.dumps(self._info(row)) + "\n"
        self.file.write(line)

        # validate
        try:
            row["prdy_ctrt"] = float(row["prdy_ctrt"])
            row["stck_prpr"] = int(row["stck_prpr"])
            row["prdy_vrss"] = int(row["prdy_vrss"])
            row["stck_bidp"] = int(row["stck_bidp"])
            row["stck_askp"] = int(row["stck_askp"])
            row["stck_vol"] = int(row["stck_vol"])
            row["stck_tr_pbmn"] = int(row["stck_tr_pbmn"])
            row["prdy_vol"] = int(row["prdy_vol"])
        except ValueError:
            raise DropItem(f"Wrong value as number type in {row}")

        return item


class StockGroupPipeline:
    def open_spider(self, spider):
        if spider.settings.get("ITEM_LIST_OUTPUT") is None:
            raise NotConfigured("ITEM_LIST_OUTPUT is not set")
        self.file = open(spider.settings.get("ITEM_LIST_OUTPUT"), "w", encoding="utf-8")

    def close_spider(self, spider):
        self.file.close()

    def _info(self, item):
        return {
            "grp_name": item["grp_name"],
            "grp_url": item["grp_url"],
        }

    def process_item(self, item, spider):
        row = ItemAdapter(item)

        # validate
        if not row["grp_url"] or not row["grp_name"] or not row["prdy_ctrt"]:
            raise DropItem(f"Empty string values in {row}")

        line = json.dumps(self._info(row)) + "\n"
        self.file.write(line)

        # validate
        try:
            row["prdy_ctrt"] = float(row["prdy_ctrt"])
            row["stck_cnt"] = int(row["stck_cnt"])
            row["incr_cnt"] = int(row["incr_cnt"])
            row["flat_cnt"] = int(row["flat_cnt"])
            row["desc_cnt"] = int(row["desc_cnt"])
        except ValueError:
            raise DropItem(f"Wrong value as number type in {row}")

        if row["stck_cnt"] == 0:
            row["stck_cnt"] = row["incr_cnt"] + row["flat_cnt"] + row["desc_cnt"]

        return item


# https://realpython.com/web-scraping-with-scrapy-and-mongodb/
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


class BasicScraperPipeline:
    def process_item(self, item, spider):
        return item
