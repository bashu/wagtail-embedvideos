# coding: utf-8

from django import forms
from django.forms.models import modelform_factory
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailimages.edit_handlers import AdminImageChooser
from wagtail.wagtailadmin.forms import (
    BaseCollectionMemberForm, collection_member_permission_formset_factory
)

from wagtail_embed_videos.models import EmbedVideo
from wagtail_embed_videos.permissions import permission_policy as embed_video_permission_policy


class BaseEmbedVideoForm(BaseCollectionMemberForm):
    permission_policy = embed_video_permission_policy


def get_embed_video_form(model):
    if hasattr(model, 'admin_form_fields'):
        fields = model.admin_form_fields
    else:
        fields = '__all__'

    if 'collection' not in fields:
        # force addition of the 'collection' field, because leaving it out can
        # cause dubious results when multiple collections exist (e.g adding the
        # media to the root collection where the user may not have permission) -
        # and when only one collection exists, it will get hidden anyway.
        fields = list(fields) + ['collection']

    return modelform_factory(
        model,
        form=BaseEmbedVideoForm,
        fields=fields,
        widgets={
            'thumbnail': AdminImageChooser,
        })


class EmbedVideoInsertionForm(forms.Form):
    alt_text = forms.CharField()


GroupEmbedVideoPermissionFormSet = collection_member_permission_formset_factory(
    EmbedVideo,
    [
        ('add_embedvideo', _("Add"), _("Add/edit video you own")),
        ('change_embedvideo', _("Edit"), _("Edit any video")),
    ],
    'wagtail_embed_videos/permissions/includes/embed_video_permissions_formset.html'
)
