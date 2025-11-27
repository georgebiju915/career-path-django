from django.db import models

# Prefer the built-in JSONField (Django 3.1+). Fall back to contrib.postgres only if needed.
try:
    # Django 3.1+ provides JSONField in django.db.models
    from django.db.models import JSONField
except ImportError:
    # Older Django (pre-3.1) - use postgres JSONField
    from django.contrib.postgres.fields import JSONField


class Company(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    website = models.URLField(null=True, blank=True)
    meta = JSONField(default=dict, blank=True)  # store scraped metadata

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class JobPosting(models.Model):
    title = models.CharField(max_length=400)
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL)
    location = models.CharField(max_length=255, blank=True)
    posted_date = models.DateField(null=True, blank=True)
    raw_html = models.TextField(blank=True)
    url = models.URLField(unique=True)
    salary = models.CharField(max_length=200, blank=True)
    parsed = JSONField(default=dict, blank=True)  # parsed fields: skills, description, seniority, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} @ {self.company or 'Unknown'}"


class ResumeProfile(models.Model):
    user_identifier = models.CharField(max_length=255, db_index=True)  # e.g., user id or upload token
    raw_text = models.TextField()
    parsed = JSONField(default=dict, blank=True)  # extracted skills, roles, experience etc.
    uploaded_at = models.DateTimeField(auto_now_add=True)


class ScrapeRun(models.Model):
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    site = models.CharField(max_length=100)
    stats = JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)