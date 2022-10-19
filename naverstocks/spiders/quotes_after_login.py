import re

import scrapy
from scrapy.http import FormRequest
from scrapy_playwright.page import PageMethod

from ..items import QuoteItem


class QuotesAfterLoginSpider(scrapy.Spider):
    """
    Usage:
        scrapy crawl quotes-after-login -O output/quotes-after-login.json
    Returns:
        100 quotes with 10 pages after login
    References:
        https://github.com/python-scrapy-playbook/scrapy-login-spiders
    """

    name = "quotes-after-login"

    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }

    re_pageId = re.compile(r'\\"productId\\":\\"([^"]+)\\"')

    def start_requests(self):
        login_url = "http://quotes.toscrape.com/login"
        yield scrapy.Request(login_url, callback=self.login)

    def login(self, response):
        token = response.css("form input[name=csrf_token]::attr(value)").extract_first()
        return FormRequest.from_response(
            response,
            formdata={"csrf_token": token, "password": "foobar", "username": "foobar"},
            callback=self.start_scraping,
        )

    def start_scraping(self, response):
        url = "https://quotes.toscrape.com"
        yield scrapy.Request(
            url,
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                playwright_page_methods=[PageMethod("wait_for_selector", "div.quote")],
                errback=self.errback,
            ),
            cb_kwargs={"page_id": 1},
        )

    async def parse(self, response, page_id: int):
        page = response.meta["playwright_page"]
        await page.screenshot(path=f"output/example-{page_id:02d}-page.png", full_page=True)
        await page.close()

        for quote in response.css("div.quote"):
            quote_item = QuoteItem()
            quote_item["text"] = quote.css("span.text::text").get()
            quote_item["author"] = quote.css("small.author::text").get()
            quote_item["tags"] = quote.css("div.tags a.tag::text").getall()
            yield quote_item

        next_page = response.css(".next>a ::attr(href)").get()
        if next_page is not None:
            found = re.search(r"/page/(\d+)/", next_page)
            if found:
                page_id = int(found.group(1))
                self.logger.info(f"next_page = {page_id!r}")

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
                cb_kwargs={"page_id": page_id},
            )

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()
