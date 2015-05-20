from __future__ import absolute_import, unicode_literals

from wagtail.wagtailadmin.edit_handlers import BaseChooserPanel
from .widgets import AdminEmbedVideoChooser


class BaseEmbedVideoChooserPanel(BaseChooserPanel):
    object_type_name = "embed_video"

    @classmethod
    def widget_overrides(cls):
        return {cls.field_name: AdminEmbedVideoChooser}


class EmbedVideoChooserPanel(object):
    def __init__(self, field_name):
        self.field_name = field_name

    def bind_to_model(self, model):
        return type(str('_EmbedVideoChooserPanel'), (BaseEmbedVideoChooserPanel,), {
            'model': model,
            'field_name': self.field_name,
        })
