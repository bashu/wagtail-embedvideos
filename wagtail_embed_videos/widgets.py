import json
from types import SimpleNamespace

from django import forms
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from embed_video.backends import detect_backend
from wagtail.admin.staticfiles import versioned_static
from wagtail.admin.widgets import AdminChooser

from wagtail_embed_videos import get_embed_video_model


class AdminEmbedVideoChooser(AdminChooser):
    choose_one_text = _("Choose an embed video")
    choose_another_text = _("Choose another embed video")
    link_to_chosen_text = _("Edit this embed video")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.embed_video_model = get_embed_video_model()

    def get_value_data(self, value):
        if value is None:
            return None
        elif isinstance(value, self.embed_video_model):
            embed_video = value
        else:  # assume embed video ID
            embed_video = self.embed_video_model.objects.get(pk=value)

        if embed_video.thumbnail:
            preview = embed_video.thumbnail.get_rendition("max-165x165")
        else:
            preview = SimpleNamespace(
                url=detect_backend(embed_video.url).get_thumbnail_url(),
                width=165,
                height=92,
            )

        return {
            "id": embed_video.pk,
            "title": embed_video.title,
            "preview": {
                "url": preview.url,
                "width": preview.width,
                "height": preview.height,
            },
            "edit_url": reverse("wagtail_embed_videos:edit", args=[embed_video.id]),
        }

    def render_html(self, name, value_data, attrs):
        value_data = value_data or {}
        original_field_html = super().render_html(name, value_data.get("id"), attrs)

        return render_to_string(
            "wagtail_embed_videos/widgets/embed_video_chooser.html",
            {
                "widget": self,
                "original_field_html": original_field_html,
                "attrs": attrs,
                "value": bool(value_data),  # only used by chooser.html to identify blank values
                "title": value_data.get("title", ""),
                "preview": value_data.get("preview", {}),
                "edit_url": value_data.get("edit_url", ""),
            },
        )

    def render_js_init(self, id_, name, value_data):
        return "createEmbedVideoChooser({0});".format(json.dumps(id_))

    @property
    def media(self):
        return forms.Media(
            js=[
                versioned_static("wagtail_embed_videos/js/embed-video-chooser-modal.js"),
                versioned_static("wagtail_embed_videos/js/embed-video-chooser.js"),
            ],
            css={
                "all": (versioned_static("wagtail_embed_videos/css/embed-video-chooser.css"),),
            },
        )
