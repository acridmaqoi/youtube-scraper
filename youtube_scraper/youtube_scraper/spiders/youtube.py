import scrapy
from scrapy_splash import SplashRequest


class YoutubeSpider(scrapy.Spider):
    name = "youtube"
    allowed_domains = ["youtube.com"]
    start_urls = ["https://www.youtube.com/watch?v=Ebme2W0yF18"]

    custom_settings = {
        # find a way to pick another video if the first one has already been scraped
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
    }

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url,
                self.parse,
                cookies={"CONSENT": "YES+"},
                args={"wait": 1.5},  # don't brute force wait for elm
            )

    def parse(self, response):
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)

        yield {
            "url": response.url,
            "embed_url": response.xpath(
                '//*[@id="watch7-content"]/link[3]//@href'
            ).get(),
            "video_id": response.xpath(
                '//*[@id="watch7-content"]/meta[5]//@content'
            ).get(),
            "name": response.xpath('//*[@id="watch7-content"]/meta[1]//@content').get(),
            "description": response.xpath(
                '//*[@id="watch7-content"]/meta[2]//@content'
            ).get(),
            "genre": response.xpath(
                '//*[@id="watch7-content"]/meta[16]//@content'
            ).get(),
            "date_published": response.xpath(
                '//*[@id="watch7-content"]/meta[14]//@content'
            ).get(),
            "genre": response.xpath(
                '//*[@id="watch7-content"]/meta[16]//@content'
            ).get(),
            "next_video_url": response.xpath(
                '//*[@id="dismissible"]/div/div[1]/a//@href'
            ).get(),
        }

        next_video = response.xpath('//*[@id="dismissible"]/div/div[1]/a//@href').get()
        if next_video is not None:
            next_video = response.urljoin(next_video)
            yield SplashRequest(next_video, self.parse, args={"wait": 1.5})
