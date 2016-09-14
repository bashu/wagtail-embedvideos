from django.contrib import admin
from django.conf import settings

from wagtail_embed_videos.models import EmbedVideo


admin.site.register(EmbedVideo)
