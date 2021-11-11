from django import forms
from django.conf import settings
from django.forms.models import modelform_factory
from django.utils.translation import gettext as _
from wagtail.admin import widgets
from wagtail.admin.forms.collections import (
    BaseCollectionMemberForm,
    CollectionChoiceField,
    collection_member_permission_formset_factory,
)
from wagtail.core.models import Collection
from wagtail.images.edit_handlers import AdminImageChooser

from wagtail_embed_videos.models import EmbedVideo
from wagtail_embed_videos.permissions import permission_policy as embed_videos_permission_policy


# Callback to allow us to override the default form field for the collection field.
def formfield_for_dbfield(db_field, **kwargs):
    # Check if this is the collection field
    if db_field.name == "collection":
        return CollectionChoiceField(
            label=_("Collection"), queryset=Collection.objects.all(), empty_label=None, **kwargs
        )

    # For all other fields, just call its formfield() method.
    return db_field.formfield(**kwargs)


class BaseEmbedVideoForm(BaseCollectionMemberForm):
    permission_policy = embed_videos_permission_policy

    class Meta:
        widgets = {
            "tags": widgets.AdminTagWidget,
            "thumbnail": AdminImageChooser,
        }


def get_embed_video_base_form():
    base_form_override = getattr(settings, "WAGTAILEMBEDVIDEOS_EMBEDVIDEO_FORM_BASE", "")
    if base_form_override:
        from django.utils.module_loading import import_string

        base_form = import_string(base_form_override)
    else:
        base_form = BaseEmbedVideoForm
    return base_form


def get_embed_video_form(model):
    fields = model.admin_form_fields
    if "collection" not in fields:
        # force addition of the 'collection' field, because leaving it out can
        # cause dubious results when multiple collections exist (e.g adding the
        # document to the root collection where the user may not have permission) -
        # and when only one collection exists, it will get hidden anyway.
        fields = list(fields) + ["collection"]

    return modelform_factory(
        model,
        form=get_embed_video_base_form(),
        fields=fields,
        formfield_callback=formfield_for_dbfield,
    )


class EmbedVideoInsertionForm(forms.Form):
    alt_text = forms.CharField()


GroupEmbedVideoPermissionFormSet = collection_member_permission_formset_factory(
    EmbedVideo,
    [
        ("add_embedvideo", _("Add"), _("Add/edit embed videos you own")),
        ("change_embedvideo", _("Edit"), _("Edit any embed video")),
        ("choose_embedvideo", _("Choose"), _("Select embed videos in choosers")),
    ],
    "wagtail_embed_videos/permissions/includes/embedvideo_permissions_formset.html",
)
