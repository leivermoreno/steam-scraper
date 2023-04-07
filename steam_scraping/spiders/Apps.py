from scrapy import Spider, Request
from scrapy.http import TextResponse

from steam_scraping.db import db
from steam_scraping.items import AppLoader


def filter_by_status(status: str, data: dict) -> bool:
    if data['status'] == status:
        return True


class AppsSpider(Spider):
    name = "apps"
    allowed_domains = ['steampowered.com', 'steamstatic.com']

    def __init__(self, status: str = 'pending', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = status
        self.db = db

    def start_requests(self):
        statuses = ['pending', 'complete', 'failed', 'partial']
        status = self.status
        if status not in statuses:
            raise ValueError(f'Status argument must be in {statuses}.')

        apps = self.db.get_by_query(lambda data: filter_by_status(status, data))

        url = "https://store.steampowered.com/app/"

        for db_id, app in apps.items():
            app_url = url + str(app["appid"])

            yield Request(app_url, callback=self.parse, errback=self.errback,
                          cb_kwargs={'db_id': db_id, 'app_id': app['appid']})

    def errback(self, failure):
        request = failure.request
        db_id = request.cb_kwargs['db_id']
        url = request.url
        err_msg = failure.getErrorMessage()

        self.db.update_by_id(db_id,
                             {'status': 'failed', 'err_msg': err_msg})
        self.logger.info(f'{url} failed to be scraped: {err_msg}')

    def get_media_links(self, response: TextResponse):
        # preview media
        preview_section = response.css('#game_highlights')
        main_image_selector = '.game_header_image_full::attr("src")'
        preview_img_selector = '.highlight_screenshot a::attr("href")'
        preview_videos_selector = '.highlight_movie::attr("data-mp4-hd-source")'
        links = preview_section.css(
            ', '.join([main_image_selector, preview_img_selector, preview_videos_selector])).getall()

        # description section media
        description_section = response.css('#aboutThisGame')
        description_img_gif_selector = 'img::attr("src")'
        links += description_section.css(description_img_gif_selector).getall()

        return links

    def load_item(self, response: TextResponse, app_id, db_id, urls):
        loader = AppLoader(response=response)
        loader.add_value('app_id', app_id)
        loader.add_value('db_id', db_id)
        loader.add_css('game_title', '#appHubAppName::text')
        loader.add_css('publisher', '#game_highlights .dev_row+ .dev_row a::text')
        loader.add_css('developer', '#developers_list a::text')
        loader.add_css('publish_date', '.date::text')
        loader.add_css('tags', '#glanceCtnResponsiveRight a::text')
        loader.add_value('file_urls', urls)

        return loader.load_item()

    def parse(self, response, db_id, app_id):
        self.db.update_by_id(db_id, {'status': 'partial'})

        links = self.get_media_links(response)
        return self.load_item(response, app_id, db_id, links)
