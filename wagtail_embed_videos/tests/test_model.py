import contextlib
import sys

from django.test import TestCase

from wagtail.images import get_image_model
from wagtail.images import get_image_model_string

from wagtail_embed_videos.models import EmbedVideo


class EmbedVideoTestCase(TestCase):
    def test_default_image_model(self):
        """Image model is the default Wagtail model"""
        # Remove module from cache
        # (https://docs.python.org/3/reference/import.html#the-module-cache)
        with contextlib.suppress(KeyError):
            del sys.modules["wagtail_embed_videos.models"]

        assert get_image_model_string() == "wagtailimages.Image"

    def test_custom_image_model(self):
        """Image model is a custom model"""
        with self.settings(WAGTAILIMAGES_IMAGE_MODEL="testapp.CustomImage"):
            with contextlib.suppress(KeyError):
                del sys.modules["wagtail_embed_videos.models"]

            assert get_image_model_string() == "testapp.CustomImage"

    def test_create_thumbnail(self):
        """Fetch a thumbnail from a video service."""
        video = EmbedVideo.objects.create(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            title="Click Me!",
        )

        assert video.thumbnail.title == "Click Me!"
        assert isinstance(video.thumbnail, get_image_model())
