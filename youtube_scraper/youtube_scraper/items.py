from dataclasses import dataclass
from datetime import datetime


class Video:
    url: str
    embed_url: str
    video_id: str
    name: str
    description: str
    thumbnail_url: str
    channel: str
    date_published: datetime
    genre: str
