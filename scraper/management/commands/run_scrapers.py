from django.core.management.base import BaseCommand
from scraper.tasks import run_naukri_scrape

class Command(BaseCommand):
    help = "Enqueue scrapers for immediate execution (example)."

    def add_arguments(self, parser):
        parser.add_argument("--keywords", required=True)
        parser.add_argument("--location", required=False)

    def handle(self, *args, **options):
        keywords = options["keywords"]
        location = options.get("location")
        run_naukri_scrape.delay(keywords, location)
        self.stdout.write(self.style.SUCCESS(f"Enqueued Naukri scraper for '{keywords}'"))