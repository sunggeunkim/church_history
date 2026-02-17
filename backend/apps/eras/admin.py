"""Admin interface for eras app."""

from django.contrib import admin

from .models import Era, KeyEvent, KeyFigure


class KeyEventInline(admin.TabularInline):
    """Inline admin for key events."""

    model = KeyEvent
    extra = 1
    fields = ["year", "title", "description", "order"]
    ordering = ["order", "year"]


class KeyFigureInline(admin.TabularInline):
    """Inline admin for key figures."""

    model = KeyFigure
    extra = 1
    fields = ["name", "birth_year", "death_year", "title", "description", "order"]
    ordering = ["order", "birth_year"]


@admin.register(Era)
class EraAdmin(admin.ModelAdmin):
    """Admin interface for Era model."""

    list_display = ["name", "start_year", "end_year", "color", "order"]
    list_editable = ["order"]
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ["name", "description"]
    ordering = ["order", "start_year"]
    inlines = [KeyEventInline, KeyFigureInline]

    fieldsets = [
        (
            "Basic Information",
            {
                "fields": ["name", "slug", "start_year", "end_year", "color", "order"],
            },
        ),
        (
            "Content",
            {
                "fields": ["summary", "description", "image_url"],
            },
        ),
    ]


@admin.register(KeyEvent)
class KeyEventAdmin(admin.ModelAdmin):
    """Admin interface for KeyEvent model."""

    list_display = ["title", "era", "year", "order"]
    list_filter = ["era"]
    search_fields = ["title", "description"]
    ordering = ["era__order", "order", "year"]


@admin.register(KeyFigure)
class KeyFigureAdmin(admin.ModelAdmin):
    """Admin interface for KeyFigure model."""

    list_display = ["name", "era", "birth_year", "death_year", "title", "order"]
    list_filter = ["era"]
    search_fields = ["name", "title", "description"]
    ordering = ["era__order", "order", "birth_year"]
