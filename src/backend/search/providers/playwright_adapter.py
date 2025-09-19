from playwright.sync_api import sync_playwright
from typing import Dict


def scrape_with_playwright(url: str) -> Dict[str, str]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        content = page.content()
        title = page.title()
        browser.close()
        return {"url": url, "title": title, "html": content}
