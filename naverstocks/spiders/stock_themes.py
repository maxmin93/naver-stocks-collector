import re

import scrapy
from scrapy.utils.log import configure_logging

from ..items import StockGroupItem
from ..pipelines import StockGroupPipeline


class NaverStockThemes(scrapy.Spider):
    """네이버 금융 > 국내증시 > 테마별 시세

    Usage:
        scrapy crawl naver-stock-themes
    Ouputs:
        - output/theme-groups.jl : json list
        - output/stock-themes.csv : csv separated by pipe(|)
    """

    configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})

    name = "naver-stock-themes"
    allowed_domains = ["finance.naver.com"]
    start_urls = [
        "https://finance.naver.com/sise/theme.naver",
    ]

    # for cleansing, validating, storing
    custom_settings = {
        "ITEM_PIPELINES": {StockGroupPipeline: 100},
        "FEEDS": {"output/stock-themes.csv": {"format": "csv", "overwrite": True}},
        "ITEM_LIST_OUTPUT": "output/theme-groups.jl",  # json list
    }

    # Rule[LinkExtractor] is not proper for this site
    # https://medium.com/quick-code/python-scrapy-tutorial-for-beginners-04-crawler-rules-and-linkextractor-7a79aeb8d72

    # constants
    col_size = len(StockGroupItem.fields)

    def parse(self, response):
        """parse data from table and extract next page"""

        # from table
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
            item["stck_cnt"] = "0"  # row[3]
            item["incr_cnt"] = row[4]
            item["flat_cnt"] = row[5]
            item["desc_cnt"] = row[6]
            yield item

        # call next request
        if (next_request := self.parse_navigation(response)) is not None:
            yield next_request

    def parse_navigation(self, response):
        """request next page from page navigation"""
        next_selector = response.xpath(
            '//div[@id="contentarea_left"]/table[@class="Nnavi"]/tr/td[@class="on"]/following-sibling::td[not(@class)]'
        )
        if not next_selector:
            self.logger.info("No more pages")
            return

        if (next_url := next_selector[0].xpath(".//a/@href").get()) is not None:
            # remove spaces, ex) ['\n\t\t\t\t', '7', '\n\t\t\t\t']
            page_text = re.sub(r"\s", "", "".join(next_selector[0].css("*::text").getall()))
            self.logger.info(f"Next page is {page_text!r}")
            return scrapy.Request(response.urljoin(next_url), callback=self.parse)

    def get_rows_from_table(self, selector):
        """parse href and td texts from each tr"""
        rows = []
        for tr in selector.xpath(".//tr/td[contains(@class,'number')]/.."):
            row = [tr.xpath(".//td")[0].xpath(".//a/@href").get()]  # url
            for td in tr.xpath(".//td[contains(@class,'col_type1') or contains(@class,'number')]"):
                text = re.sub(r"[\s\*\,\%]", "", "".join(td.css("*::text").getall()))
                row.append(text)
            rows.append(row)
        return rows
