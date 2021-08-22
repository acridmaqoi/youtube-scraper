from scrapy.item import Item, Field


class Video(Item):
    url: Field()
    embed_url: Field()
    video_id: Field()
    name: Field()
    description: Field()
    thumbnail_url: Field()
    channel: Field()
    date_published: Field()
    genre: Field()
