import scrapy
from scrapy_splash import SplashRequest
from youtube_scraper.items import Video


class YoutubeSpider(scrapy.Spider):
    name = "youtube"
    allowed_domains = ["youtube.com"]

    # splash auth
    http_user = "user"
    http_pass = "userpass"

    custom_settings = {
        # find a way to pick another video if the first one has already been scraped
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
    }

    splash_script = open("youtube_scraper/spiders/splash.lua", "r").read()

    def __init__(self, start_url, **kw):
        super().__init__(**kw)
        self.url = start_url

    def start_requests(self):
        yield SplashRequest(
            self.url,
            self.parse,
            endpoint="execute",
            args={"lua_source": self.splash_script},
        )

    def parse(self, response):
        yield Video(
            video_id=response.xpath(
                '//*[@id="watch7-content"]/meta[5]//@content'
            ).get(),
            url=response.url,
            embed_url=response.xpath('//*[@id="watch7-content"]/link[3]//@href').get(),
            name=response.xpath('//*[@id="watch7-content"]/meta[1]//@content').get(),
            description=response.xpath(
                '//*[@id="watch7-content"]/meta[2]//@content'
            ).get(),
            thumbnail_url=response.xpath(
                '//*[@id="watch7-content"]/span[2]/link//@href'
            ).get(),
            channel=response.xpath(
                '//*[@id="watch7-content"]/span[1]/link[2]//@content'
            ).get(),
            date_published=response.xpath(
                '//*[@id="watch7-content"]/meta[14]//@content'
            ).get(),
            genre=response.xpath('//*[@id="watch7-content"]/meta[16]//@content').get(),
        )

        next_video = response.xpath('//*[@id="dismissible"]/div/div[1]/a//@href').get()
        if next_video is not None:
            next_video = response.urljoin(next_video)
            yield SplashRequest(
                next_video,
                self.parse,
                endpoint="execute",
                args={"lua_source": self.splash_script},
            )
