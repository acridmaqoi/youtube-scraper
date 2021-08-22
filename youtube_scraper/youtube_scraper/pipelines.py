# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import psycopg2


class YoutubeScraperPipeline:

    table_name = "video"

    def __init__(self, db_host, db_port, db_user, db_pass, db_db):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_host=crawler.settings.get("DB_HOST"),
            db_port=crawler.settings.get("DB_PORT"),
            db_user=crawler.settings.get("DB_USER"),
            db_pass=crawler.settings.get("DB_PASS"),
            db_name=crawler.settings.get("DB_NAME"),
        )

    def open_spider(self, spider):
        self.conn = psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            database=self.db_name,
        )

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        video = ItemAdapter(item)

        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO %s VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    video.get("url"),
                    video.get("embed_url"),
                    video.get("video_id"),
                    video.get("name"),
                    video.get("description"),
                    video.get("tumbnail_url"),
                    video.get("channel"),
                    video.get("date_published"),
                    video.get("genre"),
                ),
            )

        return item
