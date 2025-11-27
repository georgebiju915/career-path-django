from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .forms import ResumeUploadForm, ScrapeForm
from .utils.resume_parser import parse_resume_text, extract_text_from_pdf
from .models import ResumeProfile, JobPosting, ScrapeRun, Company  # models assumed from earlier plan
from .tasks import run_naukri_scrape  # celery task from earlier plan (if exists)
import io

def upload_resume(request):
    form = ResumeUploadForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        text = form.cleaned_data.get("resume_text") or ""
        f = form.cleaned_data.get("resume_file")
        if f and not text:
            try:
                # try to extract plain text; fallback to raw bytes decode
                text = extract_text_from_pdf(f) if hasattr(f, "content_type") and "pdf" in f.content_type.lower() else f.read().decode("utf-8", errors="ignore")
            except Exception:
                try:
                    f.seek(0)
                    text = f.read().decode("utf-8", errors="ignore")
                except Exception:
                    text = ""
        parsed = parse_resume_text(text or "")
        rp = ResumeProfile.objects.create(user_identifier="manual_test", raw_text=text or "", parsed=parsed)
        messages.success(request, "Resume uploaded and parsed.")
        return redirect(reverse("scraper:resume_detail", kwargs={"pk": rp.pk}))
    return render(request, "scraper/resume_upload.html", {"form": form})

def resume_detail(request, pk):
    rp = get_object_or_404(ResumeProfile, pk=pk)
    return render(request, "scraper/resume_detail.html", {"resume": rp})

def run_scraper_view(request):
    form = ScrapeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        keywords = form.cleaned_data["keywords"]
        location = form.cleaned_data.get("location") or None
        max_results = form.cleaned_data.get("max_results") or 50
        # enqueue celery task if available
        try:
            task = run_naukri_scrape.delay(keywords, location, max_results)
            sr = ScrapeRun.objects.create(site="naukri", notes=f"enqueued task {task.id}", stats={"task_id": task.id})
            messages.success(request, f"Scrape enqueued (task id: {task.id}).")
        except Exception as e:
            # fallback: try to call synchronously if task not configured in this environment
            sr = ScrapeRun.objects.create(site="naukri", notes=f"synchronous run fallback: {e}")
            messages.warning(request, f"Could not enqueue Celery task, created ScrapeRun placeholder. Error: {e}")
        return redirect(reverse("scraper:scrape_results"))
    return render(request, "scraper/scrape_run.html", {"form": form})

def scrape_results(request):
    qs = JobPosting.objects.all().order_by("-created_at")[:200]
    return render(request, "scraper/scrape_results.html", {"postings": qs})

def trends(request):
    # very small trend computation: top skills across JobPosting.parsed->'skills'
    from collections import Counter
    counter = Counter()
    for jp in JobPosting.objects.all()[:2000]:
        parsed = jp.parsed or {}
        skills = parsed.get("skills") or []
        for s in skills:
            counter[s.lower()] += 1
    top = counter.most_common(25)
    # simple mapping for demo course recommendations
    COURSE_MAP = {
        "python": [
            {"title": "Python for Everybody (Coursera)", "url": "https://www.coursera.org/specializations/python"},
            {"title": "Complete Python Bootcamp (Udemy)", "url": "https://www.udemy.com/course/complete-python-bootcamp/"}
        ],
        "django": [
            {"title": "Django for Everybody (Coursera)", "url": "https://www.coursera.org/learn/django"},
            {"title": "Django 3 - Full Stack websites with Python", "url": "https://www.udemy.com/course/python-and-django-full-stack-web-developer-bootcamp/"}
        ],
        # add additional mappings as needed
    }
    recommendations = {skill: COURSE_MAP.get(skill.split()[0], []) for skill, _ in top[:10]}
    return render(request, "scraper/trends.html", {"top_skills": top, "recommendations": recommendations})