import scrapy
from scrapy.crawler import CrawlerProcess
from typing import List, Dict


class SimpleSpider(scrapy.Spider):
    name = "simple_spider"

    def __init__(self, start_urls: List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.results: List[Dict] = []

    def parse(self, response):
        self.results.append({
            "url": response.url,
            "title": response.xpath("//title/text()").get(),
            "text": " ".join(response.xpath("//body//text()").getall()).strip()
        })


def run_scrapy(urls: List[str]) -> List[Dict]:
    process = CrawlerProcess(settings={"LOG_LEVEL": "ERROR"})
    spider = SimpleSpider(start_urls=urls)
    process.crawl(spider)
    process.start()
    return spider.results
