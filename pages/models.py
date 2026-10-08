from django.db import models


class Page(models.Model):
    """Model to store static page content like About, Help, Support"""
    title = models.CharField(max_length=50, unique=True, help_text="Page identifier (e.g., 'about', 'help', 'support')")
    content = models.TextField(help_text="HTML content of the page")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
