from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from wagtail_embed_videos.views.bulk_actions.embed_video_bulk_action import EmbedVideoBulkAction


class CollectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['collection'] = forms.ModelChoiceField(
            queryset=EmbedVideoBulkAction.permission_policy.collections_user_has_permission_for(user, 'add')
        )


class AddToCollectionBulkAction(EmbedVideoBulkAction):
    display_name = _("Add to collection")
    action_type = "add_to_collection"
    aria_label = _("Add selected embed videos to collection")
    template_name = "wagtail_embed_videos/bulk_actions/confirm_bulk_add_to_collection.html"
    action_priority = 30
    form_class = CollectionForm
    collection = None

    def check_perm(self, embed_video):
        return self.permission_policy.user_has_permission_for_instance(self.request.user, 'change', embed_video)

    def get_form_kwargs(self):
        return {
            **super().get_form_kwargs(),
            'user': self.request.user
        }

    def get_execution_context(self):
        return {
            'collection': self.cleaned_form.cleaned_data['collection']
        }

    @classmethod
    def execute_action(cls, embed_videos, collection=None, **kwargs):
        if collection is None:
            return
        num_parent_objects = cls.get_default_model().objects.filter(pk__in=[obj.pk for obj in embed_videos]).update(collection=collection)
        return num_parent_objects, 0

    def get_success_message(self, num_parent_objects, num_child_objects):
        collection = self.cleaned_form.cleaned_data['collection']
        return ngettext(
            "%(num_parent_objects)d embed video has been added to %(collection)s",
            "%(num_parent_objects)d embed videos have been added to %(collection)s",
            num_parent_objects
        ) % {
            'num_parent_objects': num_parent_objects,
            'collection': collection.name
        }
