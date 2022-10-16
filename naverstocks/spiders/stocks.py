import datetime
import json
import re

import scrapy

# from scrapy.exceptions import StopDownload
from scrapy.utils.log import configure_logging

from ..items import StockItem
from ..pipelines import StockItemPipeline


class NaverStocks(scrapy.Spider):
    """네이버 금융 > 국내증시 > 업종별 시세 > 종목 리스트

    Usage:
        scrapy crawl naver-stocks
    Ouputs:
        - output/category-groups.jl : json list
        - output/stock-categories.csv : csv separated by pipe(|)
    """

    configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})

    name = "naver-stocks"
    allowed_domains = ["finance.naver.com"]

    # for cleansing, validating, storing
    custom_settings = {
        "ITEM_PIPELINES": {StockItemPipeline: 100},
        "FEEDS": {
            f"output/stocks-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.csv": {
                "format": "csv",
                "overwrite": True,
            }
        },
        "CATEGORY_LIST_INPUT": "output/category-groups.jl",  # json list
        "ITEM_LIST_OUTPUT": "output/stock-items.jl",  # json list
    }

    # constants
    col_size = len(StockItem.fields) - 1  # exclude stck_grp

    def start_requests(self):
        with open(self.settings.get("CATEGORY_LIST_INPUT"), "r", encoding="utf-8") as f:
            jl_data = f.read()
            for item in [json.loads(line) for line in jl_data.splitlines()]:
                url = f"https://{self.allowed_domains[0]}{item.get('grp_url')}"
                self.logger.info(f"start_requests: {item.get('grp_name')!r}\n{url}")
                yield scrapy.Request(
                    url, callback=self.parse, cb_kwargs={"grp_name": item.get("grp_name")}
                )
                # return

    def parse(self, response, grp_name):
        """parse data from table and extract next page"""
        _selector = response.xpath('(//div[@class="box_type_l"]/table[@class="type_5"])[1]')

        _rows = self.get_rows_from_table(_selector)
        for row in _rows:
            if len(row) < self.col_size:
                continue

            item = StockItem()
            item["stck_grp"] = grp_name  # 업종명
            item["stck_url"] = row[0]  # 종목 URL
            item["stck_name"] = row[1]  # 종목명
            item["stck_prpr"] = row[2]  # 현재가
            item["prdy_vrss"] = row[3]  # 전일비: 전일 대비
            item["prdy_ctrt"] = row[4]  # 등락률: 전일 대비율
            item["stck_bidp"] = row[5]  # 매수호가
            item["stck_askp"] = row[6]  # 매도호가
            item["stck_vol"] = row[7]  # 거래량
            item["stck_tr_pbmn"] = row[8]  # 거래대금(백만원)
            item["prdy_vol"] = row[9]  # 전일거래량
            yield item

    def get_rows_from_table(self, selector):
        """parse href and td texts from each tr"""
        rows = []
        for tr in selector.xpath(".//tbody/tr[contains(@onmouseover,'mouse')]"):
            row = [tr.xpath(".//td[@class='name']//a/@href").get()]  # url
            for td in tr.xpath(".//td[@class='name' or @class='number']"):
                text = re.sub(r"[\s\*\,\%]", "", "".join(td.css("*::text").getall()))
                row.append(text)
            rows.append(row)
        return rows
