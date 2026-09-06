from django import forms
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from embed_video.backends import detect_backend
from wagtail.admin.staticfiles import versioned_static
from wagtail.admin.widgets import BaseChooser
from wagtail.admin.widgets import BaseChooserAdapter
from wagtail.telepath import register

from wagtail_embed_videos import get_embed_video_model


class AdminEmbedVideoChooser(BaseChooser):
    choose_one_text = _("Choose an embed video")
    choose_another_text = _("Choose another embed video")
    link_to_chosen_text = _("Edit this embed video")
    template_name = "wagtail_embed_videos/widgets/embed_video_chooser.html"
    chooser_modal_url_name = "wagtail_embed_videos_chooser:choose"
    icon = "media"
    classname = "embed-video-chooser"
    js_constructor = "EmbedVideoChooser"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = get_embed_video_model()

    def get_value_data_from_instance(self, instance):
        data = super().get_value_data_from_instance(instance)
        if instance.thumbnail:
            preview_image = instance.thumbnail.get_rendition("max-165x165")
            preview = {
                "url": preview_image.url,
                "width": preview_image.width,
                "height": preview_image.height,
            }
        else:
            preview = {
                "url": detect_backend(instance.url).get_thumbnail_url(),
                "width": 165,
                "height": 92,
            }
        data["preview"] = preview
        return data

    def get_context(self, name, value_data, attrs):
        context = super().get_context(name, value_data, attrs)
        context["preview"] = value_data.get("preview", {})
        return context

    @property
    def media(self):
        return forms.Media(
            js=[
                versioned_static("wagtailadmin/js/chooser-widget.js"),
                versioned_static("wagtailadmin/js/chooser-modal.js"),
                versioned_static(
                    "wagtail_embed_videos/js/embed-video-chooser-modal.js",
                ),
                versioned_static("wagtail_embed_videos/js/embed-video-chooser.js"),
                versioned_static(
                    "wagtail_embed_videos/js/embed-video-chooser-telepath.js",
                ),
            ],
            css={
                "all": (
                    versioned_static(
                        "wagtail_embed_videos/css/embed-video-chooser.css",
                    ),
                ),
            },
        )


class EmbedVideoChooserAdapter(BaseChooserAdapter):
    js_constructor = "wagtail_embed_videos.widgets.AdminEmbedVideoChooser"

    @cached_property
    def media(self):
        return forms.Media(
            js=[
                versioned_static(
                    "wagtail_embed_videos/js/embed-video-chooser-modal.js",
                ),
                versioned_static("wagtail_embed_videos/js/embed-video-chooser.js"),
                versioned_static(
                    "wagtail_embed_videos/js/embed-video-chooser-telepath.js",
                ),
            ],
        )


register(EmbedVideoChooserAdapter(), AdminEmbedVideoChooser)
