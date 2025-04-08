from django.shortcuts import render
from .models import ClassifiedAd

def ad_list(request):
    ads = ClassifiedAd.objects.all().order_by('-updated_at')
    return render(request, 'scraper/ad_list.html', {'ads': ads})
