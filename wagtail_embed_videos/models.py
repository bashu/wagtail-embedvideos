# coding: utf-8
from __future__ import unicode_literals

try:
    import urllib2
except ImportError:
    import urllib3
import requests

from taggit.managers import TaggableManager

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.core.urlresolvers import reverse
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from wagtail.wagtailadmin.utils import get_object_usage
from wagtail.wagtailimages.models import Image as WagtailImage
from wagtail.wagtailsearch import index
from wagtail.wagtailsearch.queryset import SearchableQuerySetMixin

from embed_video.fields import EmbedVideoField
from embed_video.backends import detect_backend

try:
    from django.apps import apps
    get_model = apps.get_model
except ImportError:
    from django.db.models.loading import get_model

try:
    image_model_name = settings.WAGTAILIMAGES_IMAGE_MODEL
except AttributeError:
    image_model_name = 'wagtailimages.Image'


def checkUrl(url):
    r = requests.head(url)
    return int(r.status_code) < 400


YOUTUBE_RESOLUTIONS = [
    'maxresdefault.jpg',
    'sddefault.jpg',
    'mqdefault.jpg'
]


def create_thumbnail(model_instance):
    # CREATING IMAGE FROM THUMBNAIL
    backend = detect_backend(model_instance.url)
    thumbnail_url = backend.get_thumbnail_url()
    if backend.__class__.__name__ == 'YoutubeBackend':
        if thumbnail_url.endswith('hqdefault.jpg'):
            for resolution in YOUTUBE_RESOLUTIONS:
                temp_thumbnail_url = thumbnail_url.replace(
                    'hqdefault.jpg', resolution)
                if checkUrl(temp_thumbnail_url):
                    thumbnail_url = temp_thumbnail_url
                    break

    img_temp = NamedTemporaryFile(delete=True)
    try:
        img_temp.write(urllib2.urlopen(thumbnail_url).read())
    except:
        http = urllib3.PoolManager()
        img_temp.write(http.request('GET', thumbnail_url).data)
    img_temp.flush()

    image = WagtailImage(title=model_instance.title)
    image.file.save(model_instance.title + '.jpg', File(img_temp))

    model_instance.thumbnail = image
    model_instance.thumbnail.tags.add('video-thumbnail')
    model_instance.save()


class EmbedVideoQuerySet(SearchableQuerySetMixin, models.QuerySet):
    pass


@python_2_unicode_compatible
class AbstractEmbedVideo(index.Indexed, models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    url = EmbedVideoField()
    thumbnail = models.ForeignKey(
        image_model_name,
        verbose_name="Thumbnail",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, editable=False)

    tags = TaggableManager(help_text=None, blank=True, verbose_name=_('Tags'))

    objects = EmbedVideoQuerySet.as_manager()

    def get_usage(self):
        return get_object_usage(self)

    @property
    def usage_url(self):
        return reverse('wagtail_embed_videos_video_usage',
                       args=(self.id,))

    search_fields = [
        index.SearchField('title', partial_match=True, boost=10),
        index.RelatedFields('tags', [
            index.SearchField('name', partial_match=True, boost=10),
        ]),
        index.FilterField('uploaded_by_user'),
    ]

    def __str__(self):
        return self.title

    def __init__(self, *args, **kwargs):

        super(AbstractEmbedVideo, self).__init__(*args, **kwargs)
        if args:
            if args[3] is None:
                create_thumbnail(self)

    def save(self, *args, **kwargs):
        super(AbstractEmbedVideo, self).save(*args, **kwargs)
        if not self.thumbnail:
            create_thumbnail(self)

    @property
    def default_alt_text(self):
        return self.title

    def is_editable_by_user(self, user):
        if user.has_perm('wagtail_embed_videos.change_embedvideo'):
            # user has global permission to change videos
            return True
        elif user.has_perm('wagtail_embed_videos.add_embedvideo') and\
                self.uploaded_by_user == user:
            # user has video add permission, which also implicitly provides
            # permission to edit their own videos
            return True
        else:
            return False

    class Meta:
        abstract = True


class EmbedVideo(AbstractEmbedVideo):
    admin_form_fields = (
        'title',
        'url',
        'thumbnail',
        'tags',
    )


def get_embed_video_model():
    try:
        app_label, model_name =\
            settings.WAGTAILEMBEDVIDEO_VIDEO_MODEL.split('.')
    except AttributeError:
        return EmbedVideo
    except ValueError:
        raise ImproperlyConfigured(
            "WAGTAILEMBEDVIDEO_VIDEO_MODEL must be of the form \
            'app_label.model_name'")

    embed_video_model = get_model(app_label, model_name)
    if embed_video_model is None:
        raise ImproperlyConfigured(
            "WAGTAILEMBEDVIDEO_VIDEO_MODEL refers to model '%s' that has not \
            been installed" % settings.WAGTAILEMBEDVIDEO_VIDE_MODEL)
    return embed_video_model
