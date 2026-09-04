# ruff: noqa: N806, PLC0415
from django.apps import AppConfig
from django.db.models import ForeignKey

from . import get_embed_video_model


class WagtailEmbedVideosAppConfig(AppConfig):
    name = "wagtail_embed_videos"
    label = "wagtail_embed_videos"
    verbose_name = "Wagtail embed videos"
    default_auto_field = "django.db.models.AutoField"
    default_attrs = {}

    def ready(self):
        # Set up model forms to use AdminImageChooser for any ForeignKey to the
        # embed video model
        from wagtail.admin.forms.models import register_form_field_override

        from .widgets import AdminEmbedVideoChooser

        EmbedVideo = get_embed_video_model()
        register_form_field_override(
            ForeignKey,
            to=EmbedVideo,
            override={"widget": AdminEmbedVideoChooser},
        )

        from wagtail.models.reference_index import ReferenceIndex

        ReferenceIndex.register_model(get_embed_video_model())

        # TODO: implement EmbedVideoFieldComparison class
