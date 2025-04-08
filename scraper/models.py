from django.db import models

class ClassifiedAd(models.Model):
    title = models.CharField(max_length=255)
    price = models.CharField(max_length=50)
    link = models.URLField(unique=True)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # This will order the ads so that the most recent are first

    def __str__(self):
        return self.title
