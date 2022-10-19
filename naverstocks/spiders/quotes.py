import scrapy
from scrapy_playwright.page import PageMethod

from ..items import QuoteItem


class QuotesSpider(scrapy.Spider):
    """
    Usage:
        scrapy crawl quotes -O output/quotes-10-pages.json
    Returns:
        100 quotes with 10 pages
    References:
        https://scrapeops.io/python-scrapy-playbook/scrapy-playwright/
    """

    name = "quotes"

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }

    def start_requests(self):
        url = "https://quotes.toscrape.com/js/"
        yield scrapy.Request(
            url,
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                playwright_page_methods=[PageMethod("wait_for_selector", "div.quote")],
                errback=self.errback,
            ),
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.screenshot(path="output/example-10-pages.png", full_page=True)
        # screenshot contains the image's bytes : "screenshot ="
        await page.close()

        for quote in response.css("div.quote"):
            quote_item = QuoteItem()
            quote_item["text"] = quote.css("span.text::text").get()
            quote_item["author"] = quote.css("small.author::text").get()
            quote_item["tags"] = quote.css("div.tags a.tag::text").getall()
            yield quote_item

        next_page = response.css(".next>a ::attr(href)").get()
        if next_page is not None:
            next_page_url = "http://quotes.toscrape.com" + next_page
            yield scrapy.Request(
                next_page_url,
                meta=dict(
                    playwright=True,
                    playwright_include_page=True,
                    playwright_page_methods=[
                        PageMethod("wait_for_selector", "div.quote"),
                    ],
                    errback=self.errback,
                ),
            )

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
