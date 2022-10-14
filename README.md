# [maxmin93/naver-stocks-collector](https://github.com/maxmin93/naver-stocks-collector)

## About

[Scrapy](https://docs.scrapy.org/en/latest/index.html) 로 만든 [네이버-금융](https://finance.naver.com/sise/) 국내주식 주가 크롤러 (전종목)

## 1. 실행

### 1) 커맨드라인

```bash
$ scrapy list
naver-stock-categories

$ scrapy settings --get BOT_NAME
stocks-daily-collector

$ scrapy crawl naver-stock-categories
# ...

$ ls -l output
stock_categories.csv
stock_categories_2022-10-14T14-08-27.json
```

### 1) shell 실행

```bash
$ scrapy shell "https://finance.naver.com/sise/sise_group.naver\?type\=upjong"
# ...
[s] Available Scrapy objects:
[s]   scrapy     scrapy module (contains scrapy.Request, scrapy.Selector, etc)
[s]   crawler    <scrapy.crawler.Crawler object at 0x1061a82b0>
[s]   item       {}
[s]   request    <GET https://finance.naver.com/sise/sise_group.naver?type=upjong>
[s]   response   <200 https://finance.naver.com/sise/sise_group.naver?type=upjong>
[s]   settings   <scrapy.settings.Settings object at 0x1061a8550>
[s]   spider     <DefaultSpider 'default' at 0x106620a00>
[s] Useful shortcuts:
[s]   fetch(url[, redirect=True]) Fetch URL and update local objects (by default, redirects are followed)
[s]   fetch(req)                  Fetch a scrapy.Request and update local objects
[s]   shelp()           Shell help (print this help)
[s]   view(response)    View response in a browser
2022-10-13 23:32:48 [asyncio] DEBUG: Using selector: KqueueSelector

In [3]: table_selector = response.xpath('(//div[@id="contentarea_left"]/table)[1]'
   ...: )

In [4]: table_selector
Out[4]: [<Selector xpath='(//div[@id="contentarea_left"]/table)[1]' data='<table summary="업종별 전일대비 시세에 관한 표이며 등...'>]

```
