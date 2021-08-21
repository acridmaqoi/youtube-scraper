from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

process = CrawlerProcess(get_project_settings())

process.crawl(
    "youtube", start_url="https://www.youtube.com/watch?v=Ebme2W0yF18"
)  # Mandarin Click - HSK 1/2
process.crawl(
    "youtube", start_url="https://www.youtube.com/watch?v=9Vh_8dYkK_c"
)  # Mandarin Corner - Village Home
process.crawl(
    "youtube", start_url="https://www.youtube.com/watch?v=T3UWrgSoIxQ"
)  # Little Fox - Dino Buddies
process.start()
