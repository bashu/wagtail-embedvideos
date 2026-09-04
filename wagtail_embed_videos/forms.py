# ruff: noqa: N806
from django import forms
from django.conf import settings
from django.forms.models import modelform_factory
from django.utils.translation import gettext as _

from wagtail.admin.forms.collections import BaseCollectionMemberForm
from wagtail.admin.forms.collections import CollectionChoiceField
from wagtail.admin.forms.collections import collection_member_permission_formset_factory
from wagtail.admin.widgets import AdminTagWidget
from wagtail.images.widgets import AdminImageChooser
from wagtail.models import Collection
from wagtail.search import index as search_index

from wagtail_embed_videos.models import EmbedVideo
from wagtail_embed_videos.permissions import (
    permission_policy as embed_videos_permission_policy,
)


# Callback to allow us to override the default form field for the collection field.
def formfield_for_dbfield(db_field, **kwargs):
    # Check if this is the collection field
    if db_field.name == "collection":
        return CollectionChoiceField(
            label=_("Collection"),
            queryset=Collection.objects.all(),
            empty_label=None,
            **kwargs,
        )

    # For all other fields, just call its formfield() method.
    return db_field.formfield(**kwargs)


class BaseEmbedVideoForm(BaseCollectionMemberForm):
    permission_policy = embed_videos_permission_policy

    def save(self, commit=True):  # noqa: FBT002
        super().save(commit=commit)

        if commit:
            # Reindex the image to make sure all tags are indexed
            search_index.insert_or_update_object(self.instance)

        return self.instance

    class Meta:
        widgets = {
            "tags": AdminTagWidget,
            "thumbnail": AdminImageChooser,
        }


def get_embed_video_base_form():
    base_form_override = getattr(
        settings,
        "WAGTAILEMBEDVIDEOS_EMBEDVIDEO_FORM_BASE",
        "",
    )
    if base_form_override:
        from django.utils.module_loading import import_string  # noqa: PLC0415

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
        fields = [*list(fields), "collection"]

    BaseForm = get_embed_video_base_form()

    # If the base form specifies the 'tags' widget as a plain unconfigured
    # AdminTagWidget, substitute one that correctly passes the tag model used
    # on the image model.
    widgets = None
    if BaseForm._meta.widgets.get("tags") == AdminTagWidget:  # noqa: SLF001
        tag_model = model._meta.get_field("tags").related_model  # noqa: SLF001
        widgets = BaseForm._meta.widgets.copy()  # noqa: SLF001
        widgets["tags"] = AdminTagWidget(tag_model=tag_model)

    return modelform_factory(
        model,
        form=BaseForm,
        fields=fields,
        widgets=widgets,
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
