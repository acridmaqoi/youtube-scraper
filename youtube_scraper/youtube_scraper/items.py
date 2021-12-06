from dataclasses import dataclass
from datetime import date


@dataclass
class YoutubeVideo:
    id: str
    url: str
    embed_url: str
    name: str
    description: str
    thumbnail_url: str
    channel: str
    published: date
    views: int
    genre: str
