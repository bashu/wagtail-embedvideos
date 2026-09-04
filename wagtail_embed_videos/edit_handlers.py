from warnings import warn

from wagtail.admin.panels import FieldPanel
from wagtail.utils.deprecation import RemovedInWagtail50Warning


class EmbedVideoChooserPanel(FieldPanel):
    def __init__(self, *args, **kwargs):
        warn(
            "wagtail_embed_videos.edit_handlers.EmbedVideosChooserPanel is obsolete and should be replaced by wagtail.admin.panels.FieldPanel",  # noqa: E501
            category=RemovedInWagtail50Warning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)


# TODO: EmbedVideoFieldComparison
