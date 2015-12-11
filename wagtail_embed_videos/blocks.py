from django.utils.functional import cached_property

from wagtail.wagtailcore.blocks import ChooserBlock


class EmbedVideoChooserBlock(ChooserBlock):
    @cached_property
    def target_model(self):
        from wagtail_embed_videos.models import get_embed_video_model
        return get_embed_video_model()

    @cached_property
    def widget(self):
        from wagtail_embed_videos.widgets import AdminEmbedVideoChooser
        return AdminEmbedVideoChooser

    def render_basic(self, value):
        if value:
            return value.thumbnail
        else:
            return ''
