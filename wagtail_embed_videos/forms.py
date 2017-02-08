# coding: utf-8

from django import forms
from django.forms.models import modelform_factory

from wagtail.wagtailadmin.forms import BaseCollectionMemberForm
from wagtail.wagtailimages.edit_handlers import AdminImageChooser

from .permissions import permission_policy as embed_video_permission_policy


def get_embed_video_form(model):
    fields = model.admin_form_fields

    if 'collection' not in fields:
        # force addition of the 'collection' field, because leaving it out can
        # cause dubious results when multiple collections exist (e.g adding the
        # document to the root collection where the user may not have permission) -
        # and when only one collection exists, it will get hidden anyway.
        fields = list(fields) + ['collection']

    return modelform_factory(
        model,
        form=EmbedVideoInsertionForm,
        fields=fields,
        widgets={
            'thumbnail': AdminImageChooser,
        })


class EmbedVideoInsertionForm(BaseCollectionMemberForm):
    permission_policy = embed_video_permission_policy
    alt_text = forms.CharField()
