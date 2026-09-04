from django.dispatch import receiver
from django.test.signals import setting_changed

from wagtail.core.permission_policies.collections import (
    CollectionOwnershipPermissionPolicy,
)

from wagtail_embed_videos import get_embed_video_model
from wagtail_embed_videos.models import EmbedVideo

permission_policy = None


class EmbedVideosPermissionPolicyGetter:
    """
    A helper to retrieve the current permission policy dynamically.
    Following the descriptor protocol, this should be used as a class attribute::

        class MyEmbedVideoView(PermissionCheckedMixin, ...):
            permission_policy = EmbedVideosPermissionPolicyGetter()
    """

    def __get__(self, obj, objtype=None):
        return permission_policy


def set_permission_policy():
    """Sets the permission policy for the current embed video model."""

    global permission_policy  # noqa: PLW0603
    permission_policy = CollectionOwnershipPermissionPolicy(
        get_embed_video_model(),
        auth_model=EmbedVideo,
        owner_field_name="uploaded_by_user",
    )


@receiver(setting_changed)
def update_permission_policy(signal, sender, setting, **kwargs):
    """
    Updates the permission policy when the `WAGTAILEMBEDVIDEOS_EMBEDVIDEO_MODEL`
    setting changes. This is useful in tests where we override the base embed video
    model and expect the permission policy to have changed accordingly.
    """

    if setting == "WAGTAILEMBEDVIDEOS_EMBEDVIDEO_MODEL":
        set_permission_policy()


# Set the permission policy for the first time.
set_permission_policy()
