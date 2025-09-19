import json
import os

import redis
from dotenv import load_dotenv
from fastapi import HTTPException

from backend.schemas import SearchResponse
from backend.search.providers.base import SearchProvider
from backend.search.providers.bing import BingSearchProvider
from backend.search.providers.searxng import SearxngSearchProvider
from backend.search.providers.serper import SerperSearchProvider
from backend.search.providers.tavily import TavilySearchProvider

# New providers
from backend.search.providers.crawl4ai import Crawl4AIProvider
from backend.search.providers.firecrawl import FirecrawlProvider
from backend.scrapers.scrapy_adapter import run_scrapy
from backend.scrapers.playwright_adapter import scrape_with_playwright
from backend.scrapers.bs4_parser import parse_html

load_dotenv()


redis_url = os.getenv("REDIS_URL")
redis_client = redis.Redis.from_url(redis_url) if redis_url else None


def get_searxng_base_url():
    searxng_base_url = os.getenv("SEARXNG_BASE_URL")
    if not searxng_base_url:
        raise HTTPException(
            status_code=500,
            detail="SEARXNG_BASE_URL is not set in the environment variables.",
        )
    return searxng_base_url


def get_tavily_api_key():
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        raise HTTPException(
            status_code=500,
            detail="Tavily API key is not set in the environment variables.",
        )
    return tavily_api_key


def get_serper_api_key():
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        raise HTTPException(
            status_code=500,
            detail="Serper API key is not set in the environment variables.",
        )
    return serper_api_key


def get_bing_api_key():
    bing_api_key = os.getenv("BING_API_KEY")
    if not bing_api_key:
        raise HTTPException(
            status_code=500,
            detail="Bing API key is not set in the environment variables.",
        )
    return bing_api_key


def get_search_provider() -> SearchProvider:
    search_provider = os.getenv("SEARCH_PROVIDER", "searxng")

    match search_provider:
        case "searxng":
            searxng_base_url = get_searxng_base_url()
            return SearxngSearchProvider(searxng_base_url)
        case "tavily":
            return TavilySearchProvider(get_tavily_api_key())
        case "serper":
            return SerperSearchProvider(get_serper_api_key())
        case "bing":
            return BingSearchProvider(get_bing_api_key())
        case "crawl4ai":
            # No API key required for localhost
            return Crawl4AIProvider()
        case "firecrawl":
            # No API key required for localhost
            return FirecrawlProvider()
        case "scrapy":
            # Adapter to wrap Scrapy inside SearchProvider
            class ScrapyProvider(SearchProvider):
                async def search(self, query: str) -> SearchResponse:
                    results = run_scrapy([query])
                    return SearchResponse(results=results)
            return ScrapyProvider()
        case "playwright":
            class PlaywrightProvider(SearchProvider):
                async def search(self, query: str) -> SearchResponse:
                    data = scrape_with_playwright(query)
                    return SearchResponse(results=[data])
            return PlaywrightProvider()
        case "bs4":
            class BS4Provider(SearchProvider):
                async def search(self, query: str) -> SearchResponse:
                    # Assume query is URL
                    import requests
                    resp = requests.get(query, timeout=20)
                    parsed = parse_html(resp.text, url=query)
                    return SearchResponse(results=[parsed])
            return BS4Provider()
        case _:
            raise HTTPException(
                status_code=500,
                detail="Invalid search provider. Set SEARCH_PROVIDER to one of: "
                       "'searxng', 'tavily', 'serper', 'bing', "
                       "'crawl4ai', 'firecrawl', 'scrapy', 'playwright', 'bs4'.",
            )


async def perform_search(query: str) -> SearchResponse:
    search_provider = get_search_provider()

    try:
        cache_key = f"search:{query}"
        if redis_client and (cached_results := redis_client.get(cache_key)):
            cached_json = json.loads(json.loads(cached_results.decode("utf-8")))  # type: ignore
            return SearchResponse(**cached_json)

        results = await search_provider.search(query)

        if redis_client:
            redis_client.set(cache_key, json.dumps(results.model_dump_json()), ex=7200)

        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"There was an error while searching: {e}",
        )            detail="Tavily API key is not set in the environment variables. Please set the TAVILY_API_KEY environment variable or set SEARCH_PROVIDER to 'searxng' or 'serper'.",
        )
    return tavily_api_key


def get_serper_api_key():
    serper_api_key = os.getenv("SERPER_API_KEY")
    if not serper_api_key:
        raise HTTPException(
            status_code=500,
            detail="Serper API key is not set in the environment variables. Please set the SERPER_API_KEY environment variable or set SEARCH_PROVIDER to 'searxng' or 'tavily'.",
        )
    return serper_api_key


def get_bing_api_key():
    bing_api_key = os.getenv("BING_API_KEY")
    if not bing_api_key:
        raise HTTPException(
            status_code=500,
            detail="Bing API key is not set in the environment variables. Please set the BING_API_KEY environment variable or set SEARCH_PROVIDER to 'searxng', 'tavily', or 'serper'.",
        )
    return bing_api_key


def get_search_provider() -> SearchProvider:
    search_provider = os.getenv("SEARCH_PROVIDER", "searxng")

    match search_provider:
        case "searxng":
            searxng_base_url = get_searxng_base_url()
            return SearxngSearchProvider(searxng_base_url)
        case "tavily":
            tavily_api_key = get_tavily_api_key()
            return TavilySearchProvider(tavily_api_key)
        case "serper":
            serper_api_key = get_serper_api_key()
            return SerperSearchProvider(serper_api_key)
        case "bing":
            bing_api_key = get_bing_api_key()
            return BingSearchProvider(bing_api_key)
        case _:
            raise HTTPException(
                status_code=500,
                detail="Invalid search provider. Please set the SEARCH_PROVIDER environment variable to either 'searxng', 'tavily', 'serper', or 'bing'.",
            )


async def perform_search(query: str) -> SearchResponse:
    search_provider = get_search_provider()

    try:
        cache_key = f"search:{query}"
        if redis_client and (cached_results := redis_client.get(cache_key)):
            cached_json = json.loads(json.loads(cached_results.decode("utf-8")))  # type: ignore
            return SearchResponse(**cached_json)

        results = await search_provider.search(query)

        if redis_client:
            redis_client.set(cache_key, json.dumps(results.model_dump_json()), ex=7200)

        return results
    except Exception:
        raise HTTPException(
            status_code=500, detail="There was an error while searching."
        )
