from __future__ import absolute_import, unicode_literals

from collections import OrderedDict

from rest_framework.fields import Field

from wagtail.wagtailimages.models import SourceImageIOError


# TODO: Make a properly Embed Video Field for serialiation: have to return the url and his thumbnail


class EmbedVideoField(Field):
    def __init__(self, filter_spec, *args, **kwargs):
        self.filter_spec = filter_spec
        super(EmbedVideoField, self).__init__(*args, **kwargs)

    def to_representation(self, embed_video):
        try:
            embed_video = embed_video
            thumbnail = embed_video.thumbnail.get_rendition(self.filter_spec)

            return OrderedDict([
                ('title', embed_video.title),
                ('url', embed_video.url),
                ('thumbnail', [
                    ('url', thumbnail.url),
                    ('width', thumbnail.width),
                    ('height', thumbnail.height),
                ]),
            ])
        except SourceImageIOError:
            return OrderedDict([
                ('title', embed_video.title),
                ('url', embed_video.url),
                ('error', 'SourceImageIOError'),
            ])


class EmbedVideoThumbnailField(Field):
    """
    A field that generates a rendition with the specified filter spec, and serialises
    details of that rendition.

    Example:
    "thumbnail": {
        "url": "/media/images/myimage.max-165x165.jpg",
        "width": 165,
        "height": 100
    }    If there is an error with the source image. The dict will only contain a single
    key, "error", indicating this error:
    "thumbnail": {
        "error": "SourceImageIOError"
    }
    """

    def __init__(self, filter_spec, *args, **kwargs):
        self.filter_spec = filter_spec
        super(EmbedVideoThumbnailField, self).__init__(*args, **kwargs)

    def to_representation(self, embed_video):
        try:
            thumbnail = embed_video.thumbnail.get_rendition(self.filter_spec)

            return OrderedDict([
                ('url', thumbnail.url),
                ('width', thumbnail.width),
                ('height', thumbnail.height),
            ])
        except SourceImageIOError:
            return OrderedDict([
                ('error', 'SourceImageIOError'),
            ])
