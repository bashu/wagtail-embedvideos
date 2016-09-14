from __future__ import absolute_import, unicode_literals

from collections import OrderedDict

from rest_framework.fields import Field

from ..v2.serializers import EmbedVideoSerializer


class EmbedVideoThumbnailField(Field):
    """
    A field that generates a rendition with the specified filter spec, and serialises
    details of that rendition.

    Example:
    "thumbnail": {
        "url": "/media/images/myimage.max-165x165.jpg",
        "width": 165,
        "height": 100
    }
    """

    def get_attribute(self, instance):
        return instance

    def to_representation(self, embed_video):
        thumbnail = embed_video.thumbnail

        return OrderedDict([
            ('url', thumbnail.url),
            ('width', thumbnail.width),
            ('height', thumbnail.height),
        ])


class AdminEmbedVideoSerializer(EmbedVideoSerializer):
    thumbnail = EmbedVideoThumbnailField('max-165x165', read_only=True)
