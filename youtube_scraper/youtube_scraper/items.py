from dataclasses import dataclass
from datetime import date


@dataclass
class YoutubeVideo:
    id: str
    name: str
    description: str
    thumbnail_url: str
    channel: str
    published: date
    views: int
