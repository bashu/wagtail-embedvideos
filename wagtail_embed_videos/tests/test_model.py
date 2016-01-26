import sys

from django.conf import settings
from django.test import TestCase


class EmbedVideoTestCase(TestCase):
    def setUp(self):
        pass

    def test_video_image_model(self):
        """Image model is the default Wagtail model"""
        # Remove module from cache
        # (https://docs.python.org/3/reference/import.html#the-module-cache)
        try:
            del sys.modules['wagtail_embed_videos.models']
        except KeyError:
            pass  # Nothing to do

        # Thumbnail model is set dynamically at import.
        from wagtail_embed_videos.models import image_model_name

        self.assertEqual(image_model_name, 'wagtailimages.Image')

    def test_custom_image_model(self):
        """Image model is a custom model"""
        with self.settings(
                WAGTAILIMAGES_IMAGE_MODEL='testapp.CustomImage'):
            try:
                del sys.modules['wagtail_embed_videos.models']
            except KeyError:
                pass  # Nothing to do

            from wagtail_embed_videos.models import image_model_name

            self.assertEqual(settings.WAGTAILIMAGES_IMAGE_MODEL,
                             'testapp.CustomImage')
            self.assertEqual(image_model_name,
                             'testapp.CustomImage')
