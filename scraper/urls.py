from django.urls import path
from .views import ad_list

urlpatterns = [
    path('', ad_list, name='ad_list'),
]
