import sys

from django.conf import settings
from django.test import TestCase
from mock_django.models import ModelMock
from wagtail.images import get_image_model, get_image_model_string
from wagtail_embed_videos.models import EmbedVideo, create_thumbnail


class EmbedVideoTestCase(TestCase):
    def test_default_image_model(self):
        """Image model is the default Wagtail model"""
        # Remove module from cache
        # (https://docs.python.org/3/reference/import.html#the-module-cache)
        try:
            del sys.modules["wagtail_embed_videos.models"]
        except KeyError:
            pass  # Nothing to do

        self.assertEqual(get_image_model_string(), "wagtailimages.Image")

    def test_custom_image_model(self):
        """Image model is a custom model"""
        with self.settings(WAGTAILIMAGES_IMAGE_MODEL="testapp.CustomImage"):
            try:
                del sys.modules["wagtail_embed_videos.models"]
            except KeyError:
                pass  # Nothing to do

            self.assertEqual(get_image_model_string(), "testapp.CustomImage")

    def test_create_thumbnail(self):
        """Fetch a thumbnail from a video service."""
        video = EmbedVideo.objects.create(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", title="Click Me!")

        self.assertEqual("Click Me!", video.thumbnail.title)
        self.assertIsInstance(video.thumbnail, get_image_model())
