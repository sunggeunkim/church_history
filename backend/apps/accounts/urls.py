from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("me/", views.CurrentUserView.as_view(), name="current-user"),
]
