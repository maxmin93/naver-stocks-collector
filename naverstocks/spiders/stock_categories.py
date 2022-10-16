import re

import scrapy
from scrapy.utils.log import configure_logging

from ..items import StockGroupItem
from ..pipelines import StockGroupPipeline


class NaverStockCategories(scrapy.Spider):
    """네이버 금융 > 국내증시 > 업종별 시세

    Usage:
        scrapy crawl naver-stock-categories
    Ouputs:
        - output/category-groups.jl : json list
        - output/stock-categories.csv : csv separated by pipe(|)
    """

    configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})

    name = "naver-stock-categories"
    allowed_domains = ["finance.naver.com"]
    start_urls = [
        "https://finance.naver.com/sise/sise_group.naver?type=upjong",
    ]

    # for cleansing, validating, storing
    custom_settings = {
        "ITEM_PIPELINES": {StockGroupPipeline: 100},
        "FEEDS": {"output/stock-categories.csv": {"format": "csv", "overwrite": True}},
        "ITEM_LIST_OUTPUT": "output/category-groups.jl",  # json list
    }

    # constants
    col_size = len(StockGroupItem.fields)

    def parse(self, response):
        """parse data from table"""
        _selector = response.xpath('//div[@id="contentarea_left"]/table[contains(@class,"type_1")]')
        if not _selector:
            self.logger.error("No table found")
            return

        _rows = self.get_rows_from_table(_selector)
        for row in _rows:
            if len(row) < self.col_size:
                continue

            item = StockGroupItem()
            item["grp_url"] = row[0]
            item["grp_name"] = row[1]
            item["prdy_ctrt"] = row[2]
            item["stck_cnt"] = row[3]
            item["incr_cnt"] = row[4]
            item["flat_cnt"] = row[5]
            item["desc_cnt"] = row[6]
            yield item

    def get_rows_from_table(self, selector):
        """parse href and td texts from each tr"""
        rows = []
        for tr in selector.xpath(".//tr/td[contains(@class,'number')]/.."):
            row = [tr.xpath(".//td")[0].xpath(".//a/@href").get()]  # url
            for td in tr.xpath(".//td[not(@class) or @class!='tc']"):
                text = re.sub(r"[\s\*\,\%]", "", "".join(td.css("*::text").getall()))
                row.append(text)
            rows.append(row)
        return rows
