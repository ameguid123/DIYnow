# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field
class DiynowItem(Item):
    """ creating the item with fields we will scrape from each website we visit """
    title = Field()
    url = Field()
    image_url = Field()

