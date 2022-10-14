# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import re

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class CategoryPipeline:
    def process_item(self, item, spider):
        url_prefix = f"https://{spider.allowed_domains[0]}"

        row = ItemAdapter(item)
        row["cate_url"] = re.sub(r"\s", "", row["cate_url"])
        row["cate_name"] = re.sub(r"\s", "", row["cate_name"])
        row["vart_rate"] = re.sub(r"\s", "", row["vart_rate"]).replace("%", "")

        # validate
        if not row["cate_url"] or not row["cate_name"] or not row["vart_rate"]:
            raise DropItem(f"Missing cate_url in {item}")

        row["cate_url"] = url_prefix + row["cate_url"]

        try:
            row["vart_rate"] = float(row["vart_rate"])
            row["stck_cnt"] = int(row["stck_cnt"])
            row["incr_cnt"] = int(row["incr_cnt"])
            row["flat_cnt"] = int(row["flat_cnt"])
            row["desc_cnt"] = int(row["desc_cnt"])
        except ValueError:
            raise DropItem(f"Wrong value as number type in {row}")

        return item


class ThemePipeline:
    def process_item(self, item, spider):
        return item
