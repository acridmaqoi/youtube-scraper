# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
import json
from itemadapter import ItemAdapter

from scrapy.exceptions import DropItem
import psycopg2
from youtube_transcript_api import YouTubeTranscriptApi as yts
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class YoutubeScraperPipeline:

    table_name = "video"

    def __init__(self, db_host, db_port, db_user, db_pass, db_name):
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_name = db_name

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

        try:
            subs = yts.get_transcript(
                video.get("video_id"), languages=["zh-CN"]
            )
        except (NoTranscriptFound, TranscriptsDisabled):
            raise DropItem(f"Video has no zh subs")

        with self.conn.cursor() as cur:
            try:
                cur.execute(
                    f"INSERT INTO {self.table_name} VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        video.get("video_id"),
                        video.get("url"),
                        video.get("embed_url"),
                        video.get("name"),
                        video.get("description"),
                        video.get("thumbnail_url"),
                        video.get("channel"),
                        video.get("date_published"),
                        video.get("genre"),
                        json.dumps(subs),
                    ),
                )
                self.conn.commit()
            except psycopg2.errors.UniqueViolation:
                logger.warning("duplicate video")
                self.conn.rollback()
        return item
