import scrapy
from scrapy_splash import SplashRequest


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

    splash_script = """
    function main(splash)
      splash:set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0')
      assert(splash:go(splash.args.url))
      
      while not splash:select('#dismissible > div > div.metadata.style-scope.ytd-compact-video-renderer > a') do
        splash:wait(0.001)
      end

      return {html=splash:html()}
    end
    """

    def __init__(self, start_url, **kw):
        super().__init__(**kw)
        self.url = satrt_url

    def start_requests(self):
        yield SplashRequest(
            self.url,
            self.parse,
            endpoint="execute",
            args={"lua_source": self.splash_script},
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
            yield SplashRequest(
                next_video,
                self.parse,
                endpoint="execute",
                args={"lua_source": self.splash_script},
            )
