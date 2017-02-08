from wagtail.wagtailcore.permission_policies.collections import (
    CollectionOwnershipPermissionPolicy
)
from .models import get_embed_video_model
from .models import EmbedVideo


permission_policy = CollectionOwnershipPermissionPolicy(
    get_embed_video_model(),
    auth_model=EmbedVideo,
    owner_field_name='uploaded_by_user'
)
