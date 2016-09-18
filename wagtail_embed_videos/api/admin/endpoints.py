from __future__ import absolute_import, unicode_literals

from ..v2.endpoints import ImagesAPIEndpoint
from .serializers import EmbedVideoSerializer


class EmbedVideosAdminAPIEndpoint(ImagesAPIEndpoint):
    base_serializer_class = EmbedVideoSerializer

    body_fields = ImagesAPIEndpoint.body_fields + [
        'thumbnail',
    ]

    listing_default_fields = ImagesAPIEndpoint.listing_default_fields + [
        'width',
        'height',
        'thumbnail',
    ]
