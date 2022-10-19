# [maxmin93/naver-stocks-collector](https://github.com/maxmin93/naver-stocks-collector)

## About

[Scrapy](https://docs.scrapy.org/en/latest/index.html) 로 만든 [네이버-금융](https://finance.naver.com/sise/) 국내주식 주가 크롤러 (전종목)

## 1. 설정

### 1) settings.py

스파이더의 기본 설정 항목 또는 공통적으로 사용되는 항목들을 설정

- spider 인스턴스가 생성된 이후 settings 참조가 가능하다

```python
BOT_NAME = "naver-stocks-collector"

# 스파이더 모듈 paths (load 대상)
SPIDER_MODULES = ["naverstocks.spiders"]
# 스파이더 생성자 모듈
NEWSPIDER_MODULE = "naverstocks.spiders"

# 맥북 크롬 브라우져
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"

# True 이면 로봇 정책 때문에 읽지 않음
ROBOTSTXT_OBEY = False

# Custom exporters
FEED_EXPORTERS = {
    # 분리 기호 또는 따옴표("") 사용방식 등의 csv 옵션 변경
    "csv": "naverstocks.exporters.QuoteAllCsvItemExporter",
}

# request 사이의 delay 설정 (기본값 0초)
# - 까다로운 사이트의 경우 3초 이상을 주어야 할 수도 있음
DOWNLOAD_DELAY = 0.25

# 스파이더 Hook 클래스에 커스텀 기능 구현
# https://docs.scrapy.org/en/latest/topics/extensions.html#sample-extension
MYEXT_ENABLED = True  # enable/disable the extension
MYEXT_ITEMCOUNT = 100  # how many items per log message
```

### 2) spiders 클래스 내부에서 커스텀 설정

spider 인스턴스 생성시 개별적으로 참조되는 항목들을 설정

```python
# spiders/stock_categories.py
custom_settings = {
    "ITEM_PIPELINES": {StockGroupPipeline: 100},
    "FEEDS": {"output/stock-categories.csv": {"format": "csv", "overwrite": True}},
    # 사용자 정의 설정
    "ITEM_LIST_OUTPUT": "output/category-groups.jl",  # json list
}

# spiders/stock_themes.py
custom_settings = {
    "ITEM_PIPELINES": {StockGroupPipeline: 100},
    "FEEDS": {"output/stock-themes.csv": {"format": "csv", "overwrite": True}},
    # 사용자 정의 설정
    "ITEM_LIST_OUTPUT": "output/theme-groups.jl",  # json list
}

# spiders/stocks.py
custom_settings = {
    "ITEM_PIPELINES": {StockItemPipeline: 100},
    "FEEDS": {
        # 파일명 생성에 사용할 수 있는 변수로 %(time)s, %(batch_id)d 등이 있지만
        # 기호에 알맞지 않아 사용자 설정으로 파일명 설정함
        f"output/stocks-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.csv": {
            "format": "csv",
            "overwrite": True,
        }
    },
    # 사용자 정의 설정
    "CATEGORY_LIST_INPUT": "output/category-groups.jl",  # json list
    "ITEM_LIST_OUTPUT": "output/stock-items.jl",  # json list
}
```

## 2. 스파이더 프로젝트 구성과 실행

### 1) 프로젝트 구성

- {PROJECT_ROOT}
  - scrapy.cfg : scrapy 모듈 배포를 위한 설정
  - [naverstocks] : 실질적인 프로젝트 루트
    - settings.py : 기본 설정 및 커스텀 설정
    - pipelines.py : parse 처리된 item 들을 개별 처리하는 단계
    - items.py : export 를 위한 데이터 모델
    - exporters.py : 커스텀 exporter 기능을 설정
    - extensions.py : scrapy 실행 단계별 hook 에 실행할 확장 기능 정의
    - middlewares.py : spider, downloader 실행을 대체하는 커스텀 기능 정의
    - [spiders] : 독립적인 scrapy 실행 단위
      - stocks.py : spider 또는 crawler 클래스를 상속받아 request 와 response, parse 를 정의

### 2) scrapy 실행

```bash
$ scrapy list
naver-stock-categories
naver-stock-themes
naver-stocks

$ scrapy settings --get BOT_NAME
naver-stocks-collector

# 시작 페이지 '네이버 금융 > 국내주식 > 업종별'
$ scrapy crawl naver-stock-categories
# ==> output/stock-categories.csv
# ==> output/category-groups.jl
# ...
2022-10-17 22:07:22 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/request_bytes': 330,
 'downloader/request_count': 1,
 'downloader/request_method_count/GET': 1,
 'downloader/response_bytes': 14326,
 'downloader/response_count': 1,
 'downloader/response_status_count/200': 1,
 'elapsed_time_seconds': 0.254016,
 'feedexport/success_count/FileFeedStorage': 1,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2022, 10, 17, 13, 7, 22, 455584),
 'httpcompression/response_bytes': 80678,
 'httpcompression/response_count': 1,
 'item_scraped_count': 79,
 'log_count/DEBUG': 85,
 'log_count/INFO': 11,
 'memusage/max': 74973184,
 'memusage/startup': 74973184,
 'response_received_count': 1,
 'scheduler/dequeued': 1,
 'scheduler/dequeued/memory': 1,
 'scheduler/enqueued': 1,
 'scheduler/enqueued/memory': 1,
 'start_time': datetime.datetime(2022, 10, 17, 13, 7, 22, 201568)}
2022-10-17 22:07:22 [scrapy.core.engine] INFO: Spider closed (finished)

# 시작 페이지 '네이버 금융 > 국내주식 > 테마별'
$ scrapy crawl naver-stock-themes
# ==> output/stock-themes.csv
# ==> output/theme-groups.jl
# ...
2022-10-17 22:08:20 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/request_bytes': 2915,
 'downloader/request_count': 7,
 'downloader/request_method_count/GET': 7,
 'downloader/response_bytes': 102442,
 'downloader/response_count': 7,
 'downloader/response_status_count/200': 7,
 'elapsed_time_seconds': 1.905756,
 'feedexport/success_count/FileFeedStorage': 1,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2022, 10, 17, 13, 8, 20, 732715),
 'httpcompression/response_bytes': 509366,
 'httpcompression/response_count': 7,
 'item_scraped_count': 264,
 'log_count/DEBUG': 276,
 'log_count/INFO': 18,
 'memusage/max': 75268096,
 'memusage/startup': 75268096,
 'request_depth_max': 6,
 'response_received_count': 7,
 'scheduler/dequeued': 7,
 'scheduler/dequeued/memory': 7,
 'scheduler/enqueued': 7,
 'scheduler/enqueued/memory': 7,
 'start_time': datetime.datetime(2022, 10, 17, 13, 8, 18, 826959)}
2022-10-17 22:08:20 [scrapy.core.engine] INFO: Spider closed (finished)

# 시작 페이지 대신 'output/category-groups.jl' 내용을 읽어서 크롤링 수행
$ scrapy crawl naver-stocks
# ==> output/stocks-YYYYMMDD-HHmmss.csv
# ==> output/stock-items.jl
# ...
2022-10-17 22:09:03 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/request_bytes': 30514,
 'downloader/request_count': 79,
 'downloader/request_method_count/GET': 79,
 'downloader/response_bytes': 1277025,
 'downloader/response_count': 79,
 'downloader/response_status_count/200': 79,
 'elapsed_time_seconds': 24.313566,
 'feedexport/success_count/FileFeedStorage': 1,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2022, 10, 17, 13, 9, 3, 293017),
 'httpcompression/response_bytes': 8167172,
 'httpcompression/response_count': 79,
 'item_scraped_count': 3605,
 'log_count/DEBUG': 3689,
 'log_count/INFO': 90,
 'memusage/max': 74776576,
 'memusage/startup': 74776576,
 'response_received_count': 79,
 'scheduler/dequeued': 79,
 'scheduler/dequeued/memory': 79,
 'scheduler/enqueued': 79,
 'scheduler/enqueued/memory': 79,
 'start_time': datetime.datetime(2022, 10, 17, 13, 8, 38, 979451)}
2022-10-17 22:09:03 [scrapy.core.engine] INFO: Spider closed (finished)
```

### 3) xpath 쿼리 작성시에는 shell 사용

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

In [3]: table_selector = response.xpath('//div[@id="contentarea_left"]/table[contains(@class,"type_1")]')

In [4]: table_selector
Out[4]: [<Selector xpath='(//div[@id="contentarea_left"]/table)[1]' data='<table summary="업종별 전일대비 시세에 관한 표이며 등...'>]

In [5]: exit
```

## 3. 출력 파일

전일 대비 등락률(prdy_ctrt) 은 float 로 변환 되었지만, exporter 에 의해 "%" 포맷으로 출력함

### 1) stock-categories.csv (79건)

```csv
"desc_cnt"|"flat_cnt"|"grp_name"|"grp_url"|"incr_cnt"|"prdy_ctrt"|"stck_cnt"
1|0|"생물공학"|"/sise/sise_group_detail.naver?type=upjong&no=286"|48|"8.43%"|49
1|2|"생명과학도구및서비스"|"/sise/sise_group_detail.naver?type=upjong&no=262"|28|"7.98%"|31
0|0|"양방향미디어와서비스"|"/sise/sise_group_detail.naver?type=upjong&no=300"|11|"6.37%"|11
1|2|"우주항공과국방"|"/sise/sise_group_detail.naver?type=upjong&no=284"|13|"6.09%"|16
4|3|"방송과엔터테인먼트"|"/sise/sise_group_detail.naver?type=upjong&no=285"|48|"5.83%"|55
...
```

### 2) stock-themes.csv (264건)

```csv
"desc_cnt"|"flat_cnt"|"grp_name"|"grp_url"|"incr_cnt"|"prdy_ctrt"|"stck_cnt"
0|0|"네옴시티관련주"|"/sise/sise_group_detail.naver?type=theme&no=519"|18|"8.82%"|18
3|2|"면역항암제"|"/sise/sise_group_detail.naver?type=theme&no=389"|25|"7.6%"|30
0|0|"원숭이두창"|"/sise/sise_group_detail.naver?type=theme&no=516"|18|"7.04%"|18
0|0|"야놀자관련주"|"/sise/sise_group_detail.naver?type=theme&no=483"|5|"6.68%"|5
0|0|"인터넷대표주"|"/sise/sise_group_detail.naver?type=theme&no=49"|2|"6.54%"|2
...
```

### 3) stocks-YYYYMMDD-HHmmss.csv (3605건)

```csv
"prdy_ctrt"|"prdy_vol"|"prdy_vrss"|"stck_askp"|"stck_bidp"|"stck_grp"|"stck_name"|"stck_prpr"|"stck_tr_pbmn"|"stck_url"|"stck_vol"
"29.95%"|30242301|3250|0|14100|"생물공학"|"신라젠"|14100|160416|"/item/main.naver?code=215600"|11712693
"29.74%"|233699|3450|0|15050|"생물공학"|"앱클론"|15050|5997|"/item/main.naver?code=174900"|422985
"22.03%"|978448|1280|7100|7090|"생물공학"|"유틸렉스"|7090|50336|"/item/main.naver?code=263050"|7240939
"20.66%"|378619|405|2365|2360|"생물공학"|"지니너스"|2365|24032|"/item/main.naver?code=389030"|9897013
"18.49%"|183188|2200|14100|14050|"생물공학"|"큐리언트"|14100|4346|"/item/main.naver?code=115180"|322846
...
```

## 4. scrapy_playwright 예제 (로그인)

참고: [The Python Scrapy Playbook](https://scrapeops.io/python-scrapy-playbook/)

- [유튜브 채널 - ScrapeOps](https://www.youtube.com/channel/UCWXYh1OzOoXuHKbmhPeCBZg)
- [깃허브 python-scrapy-playbook](https://github.com/python-scrapy-playbook)

### 0) [scrapy_playwright](https://github.com/scrapy-plugins/scrapy-playwright) 라이브러리

- Scrapy 에서 headless 브라우저(Chromium)를 이용해 JS 렌더링을 수행
  - [Scrapy - Using a headless browser](https://docs.scrapy.org/en/latest/topics/dynamic-content.html#using-a-headless-browser)
- 로그인, 페이지 스크롤, 클릭 등의 동작을 수행할 수 있음

### 1) quotes.py : 다음 페이지 읽기

- `div.quote` 가 나올 때까지 기다리고 (page 로딩)
  - `PageMethod("wait_for_selector", "div.quote")`
- `next_page` 를 추가 요청한다. => 10페이지

```bash
$ scrapy crawl quotes -O output/quotes-10-pages.json
```

### 2) quotes_infinitely_scrolling.py : 무한 스크롤 페이지 읽기

- `div.quote` 가 나올 때까지 기다리고 (page 로딩)
  - `PageMethod("wait_for_selector", "div.quote")`
- 페이지 맨 하단까지 스크롤 한다.
  - `PageMethod("evaluate", "window.scrollBy(0, document.body.scrollHeight)")`
- (한 페이지에 10개 항목 출력시) 11번째 `div.quote` 를 읽어들인다 (반복)

```bash
$ scrapy crawl quotes-infinitely-scrolling -O output/quotes-infinitely.json
```

### 3) quotes_basic_login.py : 로그인

- `http://quotes.toscrape.com/login` 페이지 로그인 이후
- `http://quotes.toscrape.com` 데이터 추출

```bash
$ scrapy crawl quotes-basic-login
```

### 4) quotes_after_login.py : 로그인 이후 모든 페이지 방문

- `http://quotes.toscrape.com/login` 페이지 로그인 이후
- `http://quotes.toscrape.com` 의 모든 페이지에 대해 데이터 추출
  - 스크린샷도 10페이지 모두 출력

```bash
$ scrapy crawl quotes-after-login
```
