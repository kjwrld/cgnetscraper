from django.db import models

class ClassifiedAd(models.Model):
    title = models.CharField(max_length=255)
    price = models.CharField(max_length=50)
    link = models.URLField(unique=True)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title