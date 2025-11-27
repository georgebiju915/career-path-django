from celery import shared_task
from django.utils import timezone
from .models import ScrapeRun, JobPosting, Company
from .sources.naukri_scraper import NaukriScraper

@shared_task(bind=True, acks_late=True)
def run_naukri_scrape(self, keywords, location=None, max_results=50):
    run = ScrapeRun.objects.create(site="naukri", stats={}, notes=f"keywords={keywords}")
    try:
        scraper = NaukriScraper(rate_limit_seconds=1.5)
        results = scraper.search(keywords, location=location)
        count = 0
        for r in results[:max_results]:
            try:
                html = scraper.fetch(r["url"])
                parsed = scraper.parse_job(html)
                comp, _ = Company.objects.get_or_create(name=r.get("company") or "Unknown")
                jp, created = JobPosting.objects.get_or_create(
                    url=r["url"],
                    defaults={
                        "title": r.get("title", ""),
                        "company": comp,
                        "raw_html": html,
                        "parsed": parsed
                    }
                )
                count += 1
            except Exception as e:
                # log per-job errors
                continue
        run.finished_at = timezone.now()
        run.stats = {"count": count}
        run.save()
        return {"status": "ok", "count": count}
    except Exception as e:
        run.finished_at = timezone.now()
        run.notes += f"\nerror: {e}"
        run.save()
        raise