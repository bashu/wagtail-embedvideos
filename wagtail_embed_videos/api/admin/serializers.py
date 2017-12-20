from __future__ import absolute_import, unicode_literals

from ..fields import EmbedVideoField
from ..fields import EmbedVideoThumbnailField
from ..v2.serializers import EmbedVideoSerializer


class AdminEmbedVideoSerializer(EmbedVideoSerializer):
    thumbnail = EmbedVideoThumbnailField('max-165x165', source='*', read_only=True)
    video = EmbedVideoField('max-165x165', source='*', read_only=True)
