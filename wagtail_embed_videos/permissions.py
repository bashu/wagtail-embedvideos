# -*- coding: utf-8 -*-
from wagtail.wagtailcore.permission_policies.collections import (
    CollectionOwnershipPermissionPolicy
)

from wagtail_embed_videos.models import EmbedVideo, get_embed_video_model

permission_policy = CollectionOwnershipPermissionPolicy(
    get_embed_video_model(),
    auth_model=EmbedVideo,
    owner_field_name='uploaded_by_user'
)
