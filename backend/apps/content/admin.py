from django.contrib import admin

from .models import ContentChunk, ContentItem, ContentItemTag, ContentTag, Source


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    """Admin interface for Source model."""

    list_display = ["name", "source_type", "is_active", "created_at"]
    list_filter = ["source_type", "is_active", "created_at"]
    search_fields = ["name", "url", "description"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "source_type",
                    "url",
                    "description",
                    "is_active",
                )
            },
        ),
        (
            "Configuration",
            {
                "fields": ("scrape_config",),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(ContentTag)
class ContentTagAdmin(admin.ModelAdmin):
    """Admin interface for ContentTag model."""

    list_display = ["name", "tag_type", "slug"]
    list_filter = ["tag_type"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


class ContentItemTagInline(admin.TabularInline):
    """Inline admin for ContentItemTag."""

    model = ContentItemTag
    extra = 1
    autocomplete_fields = ["tag"]


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    """Admin interface for ContentItem model."""

    list_display = [
        "title",
        "content_type",
        "source",
        "author",
        "published_date",
        "is_processed",
        "token_count",
        "created_at",
    ]
    list_filter = [
        "content_type",
        "source",
        "is_processed",
        "created_at",
        "published_date",
    ]
    search_fields = ["title", "author", "external_id", "raw_text", "processed_text"]
    readonly_fields = ["created_at", "updated_at"]
    autocomplete_fields = ["source"]
    inlines = [ContentItemTagInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "source",
                    "content_type",
                    "title",
                    "url",
                    "external_id",
                )
            },
        ),
        (
            "Content Details",
            {
                "fields": (
                    "author",
                    "published_date",
                    "raw_text",
                    "processed_text",
                )
            },
        ),
        (
            "Processing",
            {
                "fields": (
                    "is_processed",
                    "token_count",
                    "metadata",
                ),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(ContentChunk)
class ContentChunkAdmin(admin.ModelAdmin):
    """Admin interface for ContentChunk model."""

    list_display = [
        "content_item",
        "chunk_index",
        "token_count",
        "created_at",
    ]
    list_filter = ["created_at", "content_item__content_type"]
    search_fields = ["chunk_text", "content_item__title"]
    readonly_fields = ["created_at", "embedding"]
    autocomplete_fields = ["content_item"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "content_item",
                    "chunk_index",
                    "chunk_text",
                    "token_count",
                )
            },
        ),
        (
            "Vector Embedding",
            {
                "fields": ("embedding",),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("metadata", "created_at"),
                "classes": ("collapse",),
            },
        ),
    )
