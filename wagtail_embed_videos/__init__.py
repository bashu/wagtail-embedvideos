from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

default_app_config = "wagtail_embed_videos.apps.WagtailEmbedVideosAppConfig"


def get_embed_video_model_string():
    """
    Get the dotted ``app.Model`` name for the embed video model as a string.
    Useful for developers making Wagtail plugins that need to refer to the
    embed video model, such as in foreign keys, but the model itself is not required.
    """
    return getattr(settings, "WAGTAILEMBEDVIDEOS_EMBEDVIDEO_MODEL", "wagtail_embed_videos.EmbedVideo")


def get_embed_video_model():
    """
    Get the embed video model from the ``WAGTAILEMBEDVIDEOS_EMBEDVIDEO_MODEL`` setting.
    Useful for developers making Wagtail plugins that need the embed video model.
    Defaults to the standard :class:`~wagtail_embed_videos.models.EmbedVideo` model
    if no custom model is defined.
    """
    from django.apps import apps

    model_string = get_embed_video_model_string()
    try:
        return apps.get_model(model_string, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured("WAGTAILEMBEDVIDEOS_EMBEDVIDEO_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "WAGTAILEMBEDVIDEOS_EMBEDVIDEO_MODEL refers to model '%s' that has not been installed" % model_string
        )
