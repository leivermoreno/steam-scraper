# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, Join, MapCompose, Compose, Identity
from scrapy import Field
from scrapy.loader import ItemLoader


class AppItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    app_id = Field()
    db_id = Field()
    game_title = Field()
    publisher = Field()
    developer = Field()
    publish_date = Field()
    tags = Field()
    file_urls = Field()
    images_path = Field()
    videos_path = Field()


class AppLoader(ItemLoader):
    default_output_processor = TakeFirst()
    default_input_processor = TakeFirst()
    default_item_class = AppItem

    tags_in = MapCompose(str.strip)
    tags_out = Compose(Join(';'))
    file_urls_in = Identity()
    file_urls_out = Identity()
