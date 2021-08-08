import scrapy
from scrapy_splash import SplashRequest


class YoutubeSpider(scrapy.Spider):
    name = "youtube"
    allowed_domains = ["youtube.com"]
    start_urls = ["https://www.youtube.com/watch?v=Ebme2W0yF18&t=26s"]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={"wait": 0.5})

    def parse(self, response):
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
