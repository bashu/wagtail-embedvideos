from __future__ import absolute_import, unicode_literals

from ..v2.endpoints import EmbedVideosAPIEndpoint
from .serializers import AdminEmbedVideoSerializer


class EmbedVideosAdminAPIEndpoint(EmbedVideosAPIEndpoint):
    base_serializer_class = AdminEmbedVideoSerializer

    body_fields = EmbedVideosAPIEndpoint.body_fields + [
        'thumbnail',
    ]

    listing_default_fields = EmbedVideosAPIEndpoint.listing_default_fields + [
        'width',
        'height',
        'thumbnail',
    ]
