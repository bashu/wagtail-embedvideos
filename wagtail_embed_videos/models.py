# coding: utf-8

import certifi
import requests
import urllib3 as ul
from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from embed_video.backends import VideoDoesntExistException, detect_backend
from embed_video.fields import EmbedVideoField
from taggit.managers import TaggableManager
from wagtail.admin.models import get_object_usage
from wagtail.core.models import CollectionMember
from wagtail.images import get_image_model, get_image_model_string
from wagtail.search import index
from wagtail.search.queryset import SearchableQuerySetMixin

YOUTUBE_RESOLUTIONS = ["maxresdefault.jpg", "sddefault.jpg", "mqdefault.jpg"]


class EmbedVideoQuerySet(SearchableQuerySetMixin, models.QuerySet):
    pass


def create_thumbnail(model_instance):
    # CREATING IMAGE FROM THUMBNAIL
    backend = detect_backend(model_instance.url)
    try:
        thumbnail_url = backend.get_thumbnail_url()
    except VideoDoesntExistException:
        return

    if backend.__class__.__name__ == "YoutubeBackend":
        if thumbnail_url.endswith("hqdefault.jpg"):
            for resolution in YOUTUBE_RESOLUTIONS:
                temp_thumbnail_url = thumbnail_url.replace("hqdefault.jpg", resolution)
                if int(requests.head(temp_thumbnail_url).status_code) < 400:
                    thumbnail_url = temp_thumbnail_url
                    break

    http = ul.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=certifi.where())

    img_temp = NamedTemporaryFile(suffix=".jpg", delete=False)
    img_temp.write(http.request("GET", thumbnail_url).data)
    img_temp.flush()

    image = get_image_model()(title=model_instance.title)
    image.file.save(model_instance.title + ".jpg", File(img_temp))

    model_instance.thumbnail = image
    model_instance.save()


class AbstractEmbedVideo(CollectionMember, index.Indexed, models.Model):
    title = models.CharField(max_length=255, verbose_name=_("title"))
    url = EmbedVideoField()
    thumbnail = models.ForeignKey(
        get_image_model_string(),
        verbose_name=_("thumbnail"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    created_at = models.DateTimeField(verbose_name=_("created at"), auto_now_add=True, db_index=True)
    uploaded_by_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("uploaded by user"),
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
    )

    tags = TaggableManager(help_text=None, blank=True, verbose_name=_("tags"))

    objects = EmbedVideoQuerySet.as_manager()

    def get_usage(self):
        return get_object_usage(self)

    @property
    def usage_url(self):
        return reverse("wagtail_embed_videos:embed_video_usage", args=(self.id,))

    search_fields = CollectionMember.search_fields + [
        index.SearchField("title", partial_match=True, boost=10),
        index.AutocompleteField("title"),
        index.FilterField("title"),
        index.RelatedFields(
            "tags",
            [
                index.SearchField("name", partial_match=True, boost=10),
                index.AutocompleteField("name"),
            ],
        ),
        index.FilterField("uploaded_by_user"),
    ]

    def __str__(self):
        return self.title

    @property
    def default_alt_text(self):
        # by default the alt text field (used in rich text insertion) is populated
        # from the title. Subclasses might provide a separate alt field, and
        # override this
        return self.title

    def is_editable_by_user(self, user):
        from wagtail_embed_videos.permissions import permission_policy

        return permission_policy.user_has_permission_for_instance(user, "change", self)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.thumbnail:
            create_thumbnail(self)

    class Meta:
        abstract = True


class EmbedVideo(AbstractEmbedVideo):
    admin_form_fields = (
        "title",
        "url",
        "thumbnail",
        "collection",
        "tags",
    )

    class Meta(AbstractEmbedVideo.Meta):
        verbose_name = _("embed video")
        verbose_name_plural = _("embed videos")
        permissions = [
            ("choose_embedvideo", "Can choose embed video"),
        ]
