import json

import scrapy
from scrapy.http import Response, HtmlResponse
from scrapy.shell import inspect_response
from glom import glom
from glom.core import PathAccessError

from youtube_scraper.youtube_scraper.items import YoutubeVideo


class ChannelSpider(scrapy.Spider):
    name = "channel"
    allowed_domains = ["youtube.com"]
    start_urls = ["https://www.youtube.com/channel/UCVlp63hzHZx0dXSz0wT5LAQ/videos"]
    innertubeApiKey = None
    user_agent = "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"

    # debugging
    handle_httpstatus_list = [403]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url, cookies={"CONSENT": "YES+"}, callback=self.parse_inital
            )

    def parse_inital(self, response):
        # inspect_response(response, self)
        ytCfg = json.loads(
            response.xpath("/html/head/script[9]/text()").re_first(
                r"ytcfg\.set\(({.*})\)"
            )
        )
        self.innertubeApiKey = ytCfg["INNERTUBE_API_KEY"]

        initalResContext = json.loads(
            response.xpath("/html/body/script[14]/text()").re_first(
                r"var ytInitialData = ({.*})"
            )
        )

        continuationToken = glom(
            target=initalResContext,
            spec=(
                "contents.twoColumnBrowseResultsRenderer.tabs.1.tabRenderer.content."
                "sectionListRenderer.contents.0.itemSectionRenderer.contents.0."
                "gridRenderer.items.30.continuationItemRenderer."
                "continuationEndpoint.continuationCommand.token"
            ),
        )

        # videos

        yield scrapy.Request(
            f"https://www.youtube.com/youtubei/v1/browse?key={self.innertubeApiKey}",
            method="POST",
            cookies={"CONSENT": "PENDING+297"},
            headers=[("Content-Type", "application/json")],
            body=json.dumps(
                {
                    "context": {
                        "client": {
                            "clientName": "WEB",
                            "clientVersion": "2.20211119.01.00",
                        }
                    },
                    "continuation": continuationToken,
                }
            ),
            callback=self.parse_response_context,
        )

    def parse_response_context(self, response):
        # from scrapy.shell import inspect_response

        # inspect_response(response, self)
        resContext = json.loads(response.text)

        continuationItems = glom(
            target=resContext,
            spec=(
                "onResponseReceivedActions.0.appendContinuationItemsAction.continuationItems"
            ),
        )

        videos = [
            item["gridVideoRenderer"]
            for item in continuationItems
            if item.get("gridVideoRenderer")
        ]

        for video in videos:
            video_id = video["videoId"]
            yield scrapy.Request(
                f"https://www.youtube.com/watch?v={video_id}",
                cookies={"CONSENT": "YES+"},
                callback=self.parse_video,
            )
            yield {
                "video_id": video["videoId"],
                "video_title": video["title"]["runs"][0]["text"],
                "video_views": video["viewCountText"]["simpleText"],
                "video_published": "",
            }

        try:
            continuationToken = glom(
                target=resContext,
                spec=(
                    "onResponseReceivedActions.0.appendContinuationItemsAction.continuationItems.30.continuationItemRenderer."
                    "continuationEndpoint.continuationCommand.token"
                ),
            )
        except PathAccessError:
            self.close(self, "no more pages")
        else:
            yield scrapy.Request(
                f"https://www.youtube.com/youtubei/v1/browse?key={self.innertubeApiKey}",
                method="POST",
                cookies={"CONSENT": "PENDING+297"},
                headers=[("Content-Type", "application/json")],
                body=json.dumps(
                    {
                        "context": {
                            "client": {
                                "clientName": "WEB",
                                "clientVersion": "2.20211119.01.00",
                            }
                        },
                        "continuation": continuationToken,
                    }
                ),
                callback=self.parse_response_context,
            )

    def parse_video(self, response):
        pass
