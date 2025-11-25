# Create your models here.
# core/models.py
from django.db import models
from django.contrib.postgres.fields import ArrayField  # if using PostgreSQL; for MySQL use JSONField
from django.utils import timezone
from django.db.models import JSONField

class UserProfile(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    resume_text = models.TextField(null=True, blank=True)
    skills = JSONField(default=list)  # uses MySQL JSON column
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email

class JobPost(models.Model):
    source = models.CharField(max_length=100)
    url = models.TextField()
    company = models.CharField(max_length=200, null=True, blank=True)
    title = models.CharField(max_length=300, null=True, blank=True)
    raw_text = models.TextField(null=True, blank=True)
    posted_date = models.DateTimeField(null=True, blank=True)
    scraped_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} @ {self.company}"
