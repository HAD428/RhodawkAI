from bs4 import BeautifulSoup
from typing import Dict


def parse_html(raw_html: str, url: str = "") -> Dict[str, str]:
    soup = BeautifulSoup(raw_html, "lxml")

    title = soup.title.string if soup.title else "No Title"
    text = " ".join(soup.stripped_strings)

    return {
        "url": url,
        "title": title,
        "text": text,
        "links": [a["href"] for a in soup.find_all("a", href=True)]
    }
