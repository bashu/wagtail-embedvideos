from django.conf import settings
from django.contrib import admin

from wagtail_embed_videos.models import EmbedVideo

if (
    hasattr(settings, "WAGTAILEMBEDVIDEOS_EMBEDVIDEO_MODEL")
    and settings.WAGTAILEMBEDVIDEOS_EMBEDVIDEO_MODEL != "wagtail_embed_videos.EmbedVideo"
):
    # This installation provides its own custom embed video class;
    # to avoid confusion, we won't expose the unused wagtail_embed_videos.EmbedVideo class
    # in the admin.
    pass
else:
    admin.site.register(EmbedVideo)
