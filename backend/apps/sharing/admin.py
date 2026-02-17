"""Admin configuration for social sharing."""

from django.contrib import admin

from .models import ShareLink


@admin.register(ShareLink)
class ShareLinkAdmin(admin.ModelAdmin):
    list_display = [
        "token",
        "share_type",
        "sharer_display_name",
        "view_count",
        "is_active",
        "created_at",
    ]
    list_filter = ["share_type", "is_active"]
    search_fields = ["token", "sharer_display_name"]
    readonly_fields = ["token", "content_snapshot", "view_count", "created_at"]
    ordering = ["-created_at"]
