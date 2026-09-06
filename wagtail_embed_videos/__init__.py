from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_embed_video_model_string():
    """
    Get the dotted ``app.Model`` name for the embed video model as a string.
    Useful for developers making Wagtail plugins that need to refer to the
    embed video model, such as in foreign keys, but the model itself is not required.
    """
    return getattr(
        settings,
        "WAGTAILEMBEDVIDEOS_EMBEDVIDEO_MODEL",
        "wagtail_embed_videos.EmbedVideo",
    )


def get_embed_video_model():
    """
    Get the embed video model from the ``WAGTAILEMBEDVIDEOS_EMBEDVIDEO_MODEL`` setting.
    Useful for developers making Wagtail plugins that need the embed video model.
    Defaults to the standard ``wagtail_embed_videos.models.EmbedVideo`` model
    if no custom model is defined.
    """
    from django.apps import apps  # noqa: PLC0415

    model_string = get_embed_video_model_string()
    try:
        return apps.get_model(model_string, require_ready=False)
    except ValueError as exc:
        msg = "WAGTAILEMBEDVIDEOS_EMBEDVIDEO_MODEL must be of the form 'app_label.model_name'"  # noqa: E501
        raise ImproperlyConfigured(
            msg,
        ) from exc
    except LookupError as exc:
        msg = f"WAGTAILEMBEDVIDEOS_EMBEDVIDEO_MODEL refers to model '{model_string}' that has not been installed"  # noqa: E501
        raise ImproperlyConfigured(
            msg,
        ) from exc
