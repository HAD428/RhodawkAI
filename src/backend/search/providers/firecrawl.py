import requests
from typing import Dict, Any, List

class FirecrawlProvider:
    """
    Firecrawl integration for structured crawling.
    """

    BASE_URL = "http://localhost:3000/crawl"

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def crawl(self, url: str, extract_links: bool = True) -> Dict[str, Any]:
        payload = {"url": url, "extract_links": extract_links}
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

        resp = requests.post(self.BASE_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def multi_crawl(self, urls: List[str]) -> List[Dict[str, Any]]:
        return [self.crawl(url) for url in urls]
