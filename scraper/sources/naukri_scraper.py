from .base_scraper import BaseScraper
from bs4 import BeautifulSoup
import re

class NaukriScraper(BaseScraper):
    BASE = "https://www.naukri.com"

    def search(self, keywords, location=None, page=1):
        params = {"k": keywords}
        if location:
            params["l"] = location
        url = f"{self.BASE}/jobs-in-{location}" if location else f"{self.BASE}/jobs"
        html = self.fetch(url, params=params)
        soup = self.parse_html(html)
        results = []
        # NOTE: structure may change; adapt selectors after inspecting live HTML.
        for card in soup.select(".list .jobTuple"):
            link_tag = card.select_one("a")
            if not link_tag:
                continue
            href = link_tag.get("href")
            title = card.select_one("a.title")
            company = card.select_one("a.subTitle")
            results.append({
                "url": href,
                "title": title.get_text(strip=True) if title else "",
                "company": company.get_text(strip=True) if company else ""
            })
        return results

    def parse_job(self, job_html):
        soup = BeautifulSoup(job_html, "lxml")
        # minimal example: extract description & skills
        desc = soup.select_one("#jd") or soup.select_one(".description")
        skills = []
        skill_nodes = soup.select(".key-skill .chip") or soup.select(".tags .skill")
        for s in skill_nodes:
            skills.append(s.get_text(strip=True))
        return {
            "description": desc.get_text(" ", strip=True) if desc else "",
            "skills": skills
        }