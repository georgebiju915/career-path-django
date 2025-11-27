from django.urls import path
from . import views

app_name = "scraper"

urlpatterns = [
    path("resume/upload/", views.upload_resume, name="upload_resume"),
    path("resume/<int:pk>/", views.resume_detail, name="resume_detail"),
    path("scrape/run/", views.run_scraper_view, name="scrape_run"),
    path("scrape/results/", views.scrape_results, name="scrape_results"),
    path("trends/", views.trends, name="trends"),
]