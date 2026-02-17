"""URL configuration for eras app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EraViewSet

app_name = "eras"

router = DefaultRouter()
router.register(r"", EraViewSet, basename="era")

urlpatterns = [
    path("", include(router.urls)),
]
