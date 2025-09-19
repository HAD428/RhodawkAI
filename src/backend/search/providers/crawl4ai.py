import requests
from typing import List, Dict, Any

class Crawl4AIProvider:
    """
    Wrapper for Crawl4AI API (self-hosted or SaaS).
    """

    BASE_URL = "http://localhost:8000/api/v1/crawl"

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def crawl(self, url: str, depth: int = 1) -> Dict[str, Any]:
        payload = {"url": url, "depth": depth}
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

        response = requests.post(self.BASE_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def batch_crawl(self, urls: List[str], depth: int = 1) -> List[Dict[str, Any]]:
        return [self.crawl(url, depth) for url in urls]
