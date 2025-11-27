import time
import random
import requests
from bs4 import BeautifulSoup

class BaseScraper:
    DEFAULT_HEADERS = {
        "User-Agent": "career-path-bot/1.0 (+https://yourdomain.example)",
        "Accept-Language": "en-US,en;q=0.9"
    }

    def __init__(self, rate_limit_seconds=1.0, proxies=None, headers=None):
        self.rate_limit = rate_limit_seconds
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        if headers:
            self.session.headers.update(headers)
        self.proxies = proxies

    def fetch(self, url, params=None, method="GET", **kwargs):
        time.sleep(self._sleep_time())
        resp = self.session.request(method, url, params=params, proxies=self.proxies, timeout=20, **kwargs)
        resp.raise_for_status()
        return resp.text

    def parse_html(self, html):
        return BeautifulSoup(html, "lxml")

    def _sleep_time(self):
        # randomized sleep to avoid pattern
        return self.rate_limit + random.uniform(0, self.rate_limit)

    # each concrete scraper implements:
    # def search(self, query, location=None): -> list of job URLs or dicts
    # def parse_job(self, html_or_soup): -> dict with normalized fields