# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JoinScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AwardItem(scrapy.Item):
    """
    Custom item scrapy object for the Award spider.
    """
    page_url = scrapy.Field()
    category = scrapy.Field()
    title = scrapy.Field()
    reward_amount = scrapy.Field()
    associated_organizations = scrapy.Field()
    associated_locations = scrapy.Field()
    about = scrapy.Field()
    image_urls = scrapy.Field()
    date_of_birth = scrapy.Field()
