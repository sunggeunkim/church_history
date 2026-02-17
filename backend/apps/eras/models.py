"""Church history era models.

Models for defining historical eras with key events and figures.
"""

from django.db import models


class Era(models.Model):
    """A historical era in church history."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    start_year = models.IntegerField()
    end_year = models.IntegerField(
        null=True, blank=True, help_text="Null for 'present'"
    )
    description = models.TextField()
    summary = models.TextField(blank=True, help_text="Short summary for cards")
    color = models.CharField(max_length=7, help_text="Hex color code (e.g., #C2410C)")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    image_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "start_year"]

    def __str__(self):
        end = self.end_year or "present"
        return f"{self.name} ({self.start_year}-{end})"


class KeyEvent(models.Model):
    """A significant event within a historical era."""

    era = models.ForeignKey(Era, on_delete=models.CASCADE, related_name="key_events")
    year = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "year"]

    def __str__(self):
        return f"{self.year}: {self.title}"


class KeyFigure(models.Model):
    """A significant figure within a historical era."""

    era = models.ForeignKey(Era, on_delete=models.CASCADE, related_name="key_figures")
    name = models.CharField(max_length=255)
    birth_year = models.IntegerField(null=True, blank=True)
    death_year = models.IntegerField(null=True, blank=True)
    title = models.CharField(
        max_length=255, blank=True, help_text="e.g., 'Bishop of Hippo'"
    )
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "birth_year"]

    def __str__(self):
        years = ""
        if self.birth_year and self.death_year:
            years = f" ({self.birth_year}-{self.death_year})"
        elif self.birth_year:
            years = f" (b. {self.birth_year})"
        return f"{self.name}{years}"
