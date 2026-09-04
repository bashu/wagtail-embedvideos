from django.urls import include
from django.urls import path

from wagtail import urls as wagtail_urls

urlpatterns = [path("", include(wagtail_urls))]
