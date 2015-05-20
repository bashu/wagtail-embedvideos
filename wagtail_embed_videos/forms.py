# coding: utf-8

from django import forms
from django.forms.models import modelform_factory

from embed_video.admin import AdminVideoWidget


def get_embed_video_form(model):
    if hasattr(model, 'admin_form_fields'):
        fields = model.admin_form_fields
    else:
        fields = '__all__'

    return modelform_factory(
        model,
        fields=fields)


class EmbedVideoInsertionForm(forms.Form):
    alt_text = forms.CharField()
