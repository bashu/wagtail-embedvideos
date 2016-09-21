from __future__ import absolute_import, unicode_literals

from wagtail.api.v2.endpoints import BaseAPIEndpoint
from wagtail.api.v2.filters import FieldsFilter, OrderingFilter, SearchFilter

from ...models import get_embed_video_model
from .serializers import EmbedVideoSerializer


class ImagesAPIEndpoint(BaseAPIEndpoint):
    base_serializer_class = EmbedVideoSerializer
    filter_backends = [FieldsFilter, OrderingFilter, SearchFilter]
    body_fields = BaseAPIEndpoint.body_fields + ['title', 'url', 'thumbnail']
    meta_fields = BaseAPIEndpoint.meta_fields + ['tags']
    listing_default_fields = BaseAPIEndpoint.listing_default_fields + ['title', 'tags']
    nested_default_fields = BaseAPIEndpoint.nested_default_fields + ['title']
    name = 'videos'
    model = get_embed_video_model()
