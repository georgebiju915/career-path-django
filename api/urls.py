# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserProfileViewSet, JobPostViewSet

router = DefaultRouter()
router.register(r'users', UserProfileViewSet)
router.register(r'jobs', JobPostViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
