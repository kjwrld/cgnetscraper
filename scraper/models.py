from django.db import models

class ClassifiedAd(models.Model):
    title = models.CharField(max_length=255)
    price = models.CharField(max_length=100)
    link = models.URLField(unique=True)  # unique to prevent duplicates
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
