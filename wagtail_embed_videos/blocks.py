from django.utils.functional import cached_property
from embed_video.templatetags.embed_video_tags import VideoNode
from wagtail.core.blocks import ChooserBlock


class EmbedVideoChooserBlock(ChooserBlock):
    @cached_property
    def target_model(self):
        from wagtail_embed_videos.models import get_embed_video_model

        return get_embed_video_model()

    @cached_property
    def widget(self):
        from wagtail_embed_videos.widgets import AdminEmbedVideoChooser

        return AdminEmbedVideoChooser()

    def get_form_state(self, value):
        value_data = self.widget.get_value_data(value)
        if value_data is None:
            return None
        else:
            return {
                "id": value_data["id"],
                "edit_link": value_data["edit_url"],
                "title": value_data["title"],
                "preview": value_data["preview"],
            }

    def render_basic(self, value, context=None):
        if value:
            return VideoNode.embed(value.url, size="medium")
        else:
            return ""

    # TODO: implement get_comparison_class

    class Meta:
        icon = "media"
