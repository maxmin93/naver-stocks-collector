import scrapy
from scrapy.utils.log import configure_logging

from ..items import StockGroupItem
from ..pipelines import StockGroupPipeline


class NaverStockCategories(scrapy.Spider):
    """scrape first line of  quotes from `wikiquote` by
    Maynard James Keenan and save to json file"""

    configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})

    name = "naver-stock-categories"
    allowed_domains = ["finance.naver.com"]
    start_urls = [
        "https://finance.naver.com/sise/sise_group.naver?type=upjong",
    ]

    # for cleansing, validating, storing
    custom_settings = {
        "ITEM_PIPELINES": {StockGroupPipeline: 100},
        "FEEDS": {"output/stock_categories.csv": {"format": "csv", "overwrite": True}},
    }

    def parse(self, response):
        """parse data from table"""
        _selector = response.xpath('(//div[@id="contentarea_left"]/table[@class="type_1"])[1]')

        _rows = self.get_rows_from_table(_selector)
        col_size = len(StockGroupItem.fields)
        for row in _rows:
            if len(row) < col_size:
                continue

            item = StockGroupItem()
            item["grp_url"] = row[0]
            item["grp_name"] = row[1]
            item["vart_rate"] = row[2]
            item["stck_cnt"] = row[3]
            item["incr_cnt"] = row[4]
            item["flat_cnt"] = row[5]
            item["desc_cnt"] = row[6]
            yield item

    def get_rows_from_table(self, selector):
        """parse href and td texts from each tr"""
        rows = []
        for tr in selector.xpath(".//tr"):
            if len(tr.xpath(".//td")) == 0:
                continue
            row = [tr.xpath(".//td")[0].xpath(".//a/@href").get()]
            for td in tr.xpath(".//td"):
                # gather partial texts in one td
                row.append("".join(td.css("*::text").getall()))
            rows.append(row)
        return rows
