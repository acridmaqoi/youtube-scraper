from scrapy.item import Item, Field


class Video(Item):
    video_id = Field()
    url = Field()
    embed_url = Field()
    name = Field()
    description = Field()
    thumbnail_url = Field()
    channel = Field()
    date_published = Field()
    genre = Field()
