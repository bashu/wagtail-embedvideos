from __future__ import unicode_literals

from taggit.managers import TaggableManager

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.core.urlresolvers import reverse

from wagtail.wagtailadmin.taggable import TagSearchable
from wagtail.wagtailsearch import index
from wagtail.wagtailadmin.utils import get_object_usage

from embed_video.fields import EmbedVideoField


@python_2_unicode_compatible
class AbstractEmbedVideo(models.Model, TagSearchable):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    url = EmbedVideoField()
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_by_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, editable=False)

    tags = TaggableManager(help_text=None, blank=True, verbose_name=_('Tags'))

    def get_usage(self):
        return get_object_usage(self)

    @property
    def usage_url(self):
        return reverse('wagtail_embed_videos_video_usage',
                       args=(self.id,))

    search_fields = TagSearchable.search_fields + (
        index.FilterField('uploaded_by_user'),
    )

    def __str__(self):
        return self.title

    @property
    def default_alt_text(self):
        return self.title

    def is_editable_by_user(self, user):
        if user.has_perm('wagtail_embed_videos.change_video'):
            # user has global permission to change videos
            return True
        elif user.has_perm('wagtail_embed_videos.add_video') and self.uploaded_by_user == user:
            # user has video add permission, which also implicitly provides permission to edit their own videos
            return True
        else:
            return False

    class Meta:
        abstract = True


class EmbedVideo(AbstractEmbedVideo):
    admin_form_fields = (
        'title',
        'url',
        'tags',
    )


def get_embed_video_model():
    from django.conf import settings
    from django.db.models import get_model

    try:
        app_label, model_name = settings.WAGTAILEMBEDVIDEO_VIDE_MODEL.split('.')
    except AttributeError:
        return EmbedVideo
    except ValueError:
        raise ImproperlyConfigured("WAGTAILEMBEDVIDEO_VIDE_MODEL must be of the form 'app_label.model_name'")

    embed_video_model = get_model(app_label, model_name)
    if embed_video_model is None:
        raise ImproperlyConfigured("WAGTAILEMBEDVIDEO_VIDE_MODEL refers to model '%s' that has not been installed" % settings.WAGTAILEMBEDVIDEO_VIDE_MODEL)
    return embed_video_model
