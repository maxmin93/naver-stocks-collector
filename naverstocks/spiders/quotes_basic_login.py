import scrapy
from scrapy.http import FormRequest

from ..items import QuoteItem


class QuotesBasicLoginSpider(scrapy.Spider):
    """
    Usage:
        scrapy crawl quotes-basic-login -O output/quotes-after-login.json
    Returns:
        10 quotes
    References:
        https://github.com/python-scrapy-playbook/scrapy-login-spiders
    """

    name = "quotes-basic-login"

    def start_requests(self):
        login_url = "http://quotes.toscrape.com/login"
        yield scrapy.Request(login_url, callback=self.login)

    def login(self, response):
        token = response.css("form input[name=csrf_token]::attr(value)").extract_first()
        # FormRequest with hidden data (csrf_token)
        return FormRequest.from_response(
            response,
            formdata={"csrf_token": token, "password": "foobar", "username": "foobar"},
            callback=self.start_scraping,
        )

    def start_scraping(self, response):
        for quote in response.css("div.quote"):
            quote_item = QuoteItem()
            quote_item["text"] = quote.css("span.text::text").get()
            quote_item["author"] = quote.css("small.author::text").get()
            quote_item["tags"] = quote.css("div.tags a.tag::text").getall()
            yield quote_item
