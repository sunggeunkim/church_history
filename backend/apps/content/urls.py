"""URL configuration for content app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ContentItemViewSet, SourceViewSet, content_search

app_name = "content"

router = DefaultRouter()
router.register(r"sources", SourceViewSet, basename="source")
router.register(r"items", ContentItemViewSet, basename="contentitem")

urlpatterns = [
    path("", include(router.urls)),
    path("search/", content_search, name="content-search"),
]
