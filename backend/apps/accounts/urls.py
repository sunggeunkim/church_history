from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("me/", views.CurrentUserView.as_view(), name="current-user"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
]

# Google OAuth URL is registered at the project level in config/urls.py
