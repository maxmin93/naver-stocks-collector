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
    vart_rate = Field(serializer=serialize_rate)
    stck_cnt = Field(serializer=int)
    incr_cnt = Field(serializer=int)
    flat_cnt = Field(serializer=int)
    desc_cnt = Field(serializer=int)
