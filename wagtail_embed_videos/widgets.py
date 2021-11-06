import json

from django import forms
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
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

    def render_html(self, name, value, attrs):
        instance, value = self.get_instance_and_id(self.embed_video_model, value)
        original_field_html = super().render_html(name, value, attrs)

        return render_to_string(
            "wagtail_embed_videos/widgets/embed_video_chooser.html",
            {
                "widget": self,
                "original_field_html": original_field_html,
                "attrs": attrs,
                "value": value,
                "embed_video": instance,
            },
        )

    def render_js_init(self, id_, name, value):
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
