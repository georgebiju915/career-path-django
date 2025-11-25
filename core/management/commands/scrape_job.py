# core/management/commands/scrape_job.py
from django.core.management.base import BaseCommand
from core.models import JobPost
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class Command(BaseCommand):
    help = "Scrape a single job URL and save"

    def add_arguments(self, parser):
        parser.add_argument('url', type=str)

    def handle(self, *args, **options):
        url = options['url']
        r = requests.get(url, timeout=20)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.select_one('h1')
        title_text = title.get_text(strip=True) if title else url
        jp = JobPost.objects.create(source="generic", url=url, title=title_text, raw_text=r.text)
        self.stdout.write(self.style.SUCCESS(f"Saved job {jp.id}"))
