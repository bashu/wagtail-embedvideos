from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


default_app_config = 'wagtail_embed_videos.apps.WagtailEmbedVideosAppConfig'


def get_embed_video_model_string():
    """Get the dotted app.Model name for the image model"""
    return getattr(settings, 'WAGTAILEMBEDVIDEO_VIDEO_MODEL', 'wagtail_embed_videos.EmbedVideo')


def get_embed_video_model():
    """Get the image model from WAGTAILEMBEDVIDEO_VIDEO_MODEL."""
    from django.apps import apps
    model_string = get_embed_video_model_string()
    try:
        return apps.get_model(model_string)
    except ValueError:
        raise ImproperlyConfigured("WAGTAILEMBEDVIDEO_VIDEO_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "WAGTAILEMBEDVIDEO_VIDEO_MODEL refers to model '%s' that has not been installed" % model_string
        )
