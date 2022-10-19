import scrapy
from scrapy_playwright.page import PageMethod

from ..items import QuoteItem


class QuotesInfinitelyScrollingSpider(scrapy.Spider):
    """
    Usage:
        scrapy crawl quotes-infinitely-scrolling -O output/quotes.json

    References:
        https://scrapeops.io/python-scrapy-playbook/scrapy-playwright/
    """

    name = "quotes-infinitely-scrolling"

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
                playwright_page_methods=[
                    PageMethod("wait_for_selector", "div.quote"),
                    # JS: move to the bottom of the page
                    PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)"),
                    PageMethod("wait_for_selector", "div.quote:nth-child(11)"),  # 10 per page
                ],
                errback=self.errback,
            ),
        )

    async def parse(self, response):
        page = response.meta["playwright_page"]
        await page.screenshot(path="output/example.png", full_page=True)
        await page.close()

        for quote in response.css("div.quote"):
            quote_item = QuoteItem()
            quote_item["text"] = quote.css("span.text::text").get()
            quote_item["author"] = quote.css("small.author::text").get()
            quote_item["tags"] = quote.css("div.tags a.tag::text").getall()
            yield quote_item

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
