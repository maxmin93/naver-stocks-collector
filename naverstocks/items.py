# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


def serialize_rate(value):
    return f"{str(value)}%"


class StockGroupItem(scrapy.Item):
    grp_name = Field(serializer=str)
    grp_url = Field(serializer=str)
    prdy_ctrt = Field(serializer=serialize_rate)  # 등락률: 전일 대비율
    stck_cnt = Field(serializer=int)
    incr_cnt = Field(serializer=int)
    flat_cnt = Field(serializer=int)
    desc_cnt = Field(serializer=int)


# [한국투자증권 API]
#   국내주식기간별시세(일/주/월/년)[v1_국내주식-016]
#   https://apiportal.koreainvestment.com/apiservice/apiservice-domestic-stock-quotations#L_a08c3421-e50f-4f24-b1fe-64c12f723c77
class StockItem(scrapy.Item):
    stck_grp = Field(serializer=str)  # 업종명
    stck_url = Field(serializer=str)  # 종목 URL
    stck_name = Field(serializer=str)  # 종목명
    stck_prpr = Field(serializer=int)  # 현재가
    prdy_vrss = Field(serializer=int)  # 전일비: 전일 대비
    prdy_ctrt = Field(serializer=serialize_rate)  # 등락률: 전일 대비율
    stck_bidp = Field(serializer=int)  # 매수호가
    stck_askp = Field(serializer=int)  # 매도호가
    stck_vol = Field(serializer=int)  # 거래량
    stck_tr_pbmn = Field(serializer=int)  # 거래대금(백만원)
    prdy_vol = Field(serializer=int)  # 전일거래량


class QuoteItem(scrapy.Item):
    # define the fields for your item here like:
    text = scrapy.Field()
    author = scrapy.Field()
    tags = scrapy.Field()
