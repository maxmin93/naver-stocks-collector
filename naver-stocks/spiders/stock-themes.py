import re

import scrapy
from scrapy.exceptions import StopDownload
from scrapy.utils.log import configure_logging

from ..items import StockGroupItem
from ..pipelines import StockGroupPipeline


class NaverStockThemes(scrapy.Spider):
    """scrape first line of  quotes from `wikiquote` by
    Maynard James Keenan and save to json file"""

    configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})

    name = "naver-stock-themes"
    allowed_domains = ["finance.naver.com"]
    start_urls = [
        "https://finance.naver.com/sise/theme.naver",
    ]

    # for cleansing, validating, storing
    custom_settings = {
        "ITEM_PIPELINES": {StockGroupPipeline: 100},
        "FEEDS": {"output/stock_themes.csv": {"format": "csv", "overwrite": True}},
    }

    def parse(self, response):
        """parse data from table and extract next page"""

        # from table
        table_selector = response.xpath(
            '(//div[@id="contentarea_left"]/table[@class="type_1 theme"])[1]'
        )

        _rows = self.get_rows_from_table(table_selector)
        col_size = len(StockGroupItem.fields)
        for row in _rows:
            if len(row) < col_size:
                continue

            item = StockGroupItem()
            item["grp_url"] = row[0]
            item["grp_name"] = row[1]
            item["vart_rate"] = row[2]
            item["stck_cnt"] = "0"  # row[3]
            item["incr_cnt"] = row[4]
            item["flat_cnt"] = row[5]
            item["desc_cnt"] = row[6]
            yield item

        # from page navigation
        next_selector = response.xpath(
            '(//div[@id="contentarea_left"]/table[@class="Nnavi"])/tr/td[@class="on"]/following-sibling::td'
        )
        if len(next_selector) == 0:
            self.logger.info("No more pages")
            raise StopDownload(fail=False)

        if (next_url := next_selector[0].xpath(".//a/@href").get()) is not None:
            # remove spaces, ex) ['\n\t\t\t\t', '7', '\n\t\t\t\t']
            page_text = re.sub(r"\s", "", "".join(next_selector[0].css("*::text").getall()))
            self.logger.info('next page is "%s"', page_text)
            yield scrapy.Request(response.urljoin(next_url), callback=self.parse)

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
