from embed_video.templatetags.embed_video_tags import VideoNode
from wagtail.admin.ui.fields import BaseFieldDisplay


class EmbedVideoDisplay(BaseFieldDisplay):
    def render_html(self, parent_context):
        if self.value is None:
            return None
        # VideoNode.embed() already returns a mark_safe()'d string.
        return VideoNode.embed(self.value.url, size="medium", context=parent_context)
