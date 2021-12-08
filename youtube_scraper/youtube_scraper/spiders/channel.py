import json
import re

import scrapy
from scrapy.http import Response, HtmlResponse
from scrapy.shell import inspect_response
from glom import glom
from glom.core import PathAccessError


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
        inital_res_context = json.loads(
            response.xpath("/html/body").re_first(
                r"var ytInitialData = ({.*});</script>"
            )
        )

        contents = glom(
            inital_res_context,
            "contents.twoColumnWatchNextResults.results.results.contents",
        )

        video_primary_info_renderer = glom(contents, "0.videoPrimaryInfoRenderer")

        toggle_button_renderer = glom(
            video_primary_info_renderer,
            "videoActions.menuRenderer.topLevelButtons.0.toggleButtonRenderer",
        )

        video_id = glom(
            toggle_button_renderer,
            "defaultNavigationEndpoint.modalEndpoint.modal.modalWithTitleAndButtonRenderer.button.buttonRenderer.navigationEndpoint.signInEndpoint.nextEndpoint.watchEndpoint.videoId",
        )

        title = video_primary_info_renderer.get("title").get("runs")[0].get("text")
        published = video_primary_info_renderer.get("dateText").get("simpleText")
        likes = toggle_button_renderer.get("toggledText").get("simpleText")

        likes = re.search(r'"label":"(.*?) likes"', inital_res_context).group(1)
        channel = re.search(
            r'"videoOwnerRenderer".*?"title":{"runs":\[{"text":"(.*?)"',
            inital_res_context,
        ).group(1)
        thumbnail_url = re.search(
            r'thumbnails.*?{.*?},{.*?},{"url":"(.*?)","width":176,"height":176}',
            inital_res_context,
        ).group(1)

        print(video_id)

        ## ---
        # initalResContext = json.loads(
        #    response.xpath("/html/body").re_first(
        #        r"var ytInitialData = ({.*});</script>"
        #    )
        # )

        # video_contents = glom(
        #    target=initalResContext,
        #    spec=("contents.twoColumnWatchNextResults.results.results.contents"),
        # )
        # print(video_contents)

        # video_primary_info = video_contents[0]["videoPrimaryInfoRenderer"]
        # video_id = video_primary_info["videoActions"]["menuRenderer"][
        #    "topLevelButtons"
        # ][3]["downloadButtonRenderer"]["command"]["offlineVideoEndpoint"]["videoId"]

        # video_id = glom(
        #    target=video_primary_info,
        #    spec=(
        #        "videoActions.menuRenderer.topLevelButtons.3.downloadButtonRenderer.command.offlineVideo"
        #    ),
        # )
        # published = video_primary_info["dateText"]["simpleText"]
