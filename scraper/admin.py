from django.contrib import admin
from .models import ClassifiedAd

@admin.register(ClassifiedAd)
class ClassifiedAdAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'link', 'updated_at')
