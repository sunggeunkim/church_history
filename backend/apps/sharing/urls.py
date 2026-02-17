from django.urls import path

from . import views

app_name = "sharing"

urlpatterns = [
    path("links/", views.CreateShareLinkView.as_view(), name="create-link"),
    path("links/list/", views.ListShareLinksView.as_view(), name="list-links"),
    path("links/<str:token>/", views.DeleteShareLinkView.as_view(), name="delete-link"),
]
