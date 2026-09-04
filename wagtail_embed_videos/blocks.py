from django.utils.functional import cached_property

from embed_video.templatetags.embed_video_tags import VideoNode
from wagtail.blocks import ChooserBlock


class EmbedVideoChooserBlock(ChooserBlock):
    @cached_property
    def target_model(self):
        from wagtail_embed_videos import get_embed_video_model  # noqa: PLC0415

        return get_embed_video_model()

    @cached_property
    def widget(self):
        from wagtail_embed_videos.widgets import AdminEmbedVideoChooser  # noqa: PLC0415

        return AdminEmbedVideoChooser()

    def render_basic(self, value, context=None):
        if value:
            return VideoNode.embed(value.url, size="medium", context=context)
        return ""

    # TODO: implement get_comparison_class

    class Meta:
        icon = "media"
